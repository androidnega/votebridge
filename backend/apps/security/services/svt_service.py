import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MFALog, Role
from apps.accounts.services.mfa_service import MFAService
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.security.demo_svt_codes import (
    DEMO_SVT_FAR_FUTURE_YEAR,
    demo_svt_enabled,
    get_dev_demo_svt_codes,
    match_dev_demo_svt_code,
)
from apps.security.models import SVTToken
from apps.security.repositories.svt_repository import SVTRepository
from apps.security.validators import (
    validate_election_open_for_svt,
    validate_svt_for_ballot_start,
    validate_svt_for_ballot_submit,
    validate_svt_for_verification,
)
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository
from core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from core.utils.phone import mask_phone_number

logger = logging.getLogger("votebridge")


class SVTAuditService:
    """Writes SVT lifecycle events to the existing MFALog audit table."""

    def __init__(self, mfa_service: MFAService | None = None):
        self.mfa_service = mfa_service or MFAService()

    def log_issued(self, user, svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(MFALog.EventType.SVT_ISSUED, user, svt, ip_address, user_agent)

    def log_validated(self, user, svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(MFALog.EventType.SVT_VALIDATED, user, svt, ip_address, user_agent)

    def log_ballot_started(self, user, svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(MFALog.EventType.BALLOT_STARTED, user, svt, ip_address, user_agent)

    def log_ballot_submitted(self, user, svt: SVTToken, vote_count: int, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.BALLOT_SUBMITTED,
            user,
            svt,
            ip_address,
            user_agent,
            {"votes_recorded": vote_count},
        )

    def log_consumed(self, user, svt: SVTToken, vote_count: int, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.SVT_CONSUMED,
            user,
            svt,
            ip_address,
            user_agent,
            {"votes_recorded": vote_count},
        )

    def log_revoked(self, admin_user, svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.SVT_REVOKED,
            admin_user,
            svt,
            ip_address,
            user_agent,
            {"target_user_uuid": str(svt.user.uuid)},
        )

    def log_reissued(self, admin_user, old_svt: SVTToken, new_svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.SVT_REISSUED,
            admin_user,
            new_svt,
            ip_address,
            user_agent,
            {
                "old_svt_id": str(old_svt.svt_id),
                "target_user_uuid": str(new_svt.user.uuid),
            },
        )

    def log_verified(self, user, svt: SVTToken, ip_address=None, user_agent=None):
        return self._log(MFALog.EventType.SVT_VOTE_VERIFIED, user, svt, ip_address, user_agent)

    def _log(self, event_type, user, svt: SVTToken, ip_address, user_agent, metadata=None):
        return self.mfa_service.log(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "svt_id": str(svt.svt_id),
                "election_uuid": str(svt.election.uuid),
                **(metadata or {}),
            },
        )


class SVTService:
    """Generate, validate, consume, and manage Secure Voting Tokens."""

    def __init__(
        self,
        svt_repository: SVTRepository | None = None,
        election_repository: ElectionRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
        vote_repository: VoteRepository | None = None,
        audit_service: SVTAuditService | None = None,
    ):
        self.svt_repository = svt_repository or SVTRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.vote_repository = vote_repository or VoteRepository()
        self.audit_service = audit_service or SVTAuditService()

    def _user_has_submitted_ballot(self, user, election) -> bool:
        if self.svt_repository.get_queryset().filter(
            user=user,
            election=election,
            status=SVTToken.Status.USED,
        ).exists():
            return True
        positions = self.eligibility_repository.get_eligible_positions_for_user(election, user)
        position_list = list(positions)
        if not position_list:
            return False
        return all(
            self.vote_repository.count_for_user_position(user, position)
            >= (position.max_votes_allowed or 1)
            for position in position_list
        )

    def _log_dev_svt_code(self, user, election, plain_code: str, expires_at) -> None:
        """Development only — print voting code to the runserver terminal for manual copy."""
        if not settings.DEBUG:
            return
        demo_codes = get_dev_demo_svt_codes() if demo_svt_enabled() else []
        demo_block = ""
        if demo_codes:
            demo_block = (
                "\n  Demo pool (no expiry — one election per code per student):\n    "
                + "\n    ".join(demo_codes)
                + "\n"
            )
        logger.warning(
            "\n========== DEV VOTING CODE (copy from terminal) ==========\n"
            "  Election: %s\n"
            "  User:     %s\n"
            "  Code:     %s\n"
            "  Expires:  %s\n"
            "%s"
            "==========================================================",
            election.title,
            user.email or user.uuid,
            plain_code,
            expires_at.strftime("%H:%M"),
            demo_block,
        )

    def _send_svt_sms(self, user, election, plain_code: str, expires_at) -> None:
        self._log_dev_svt_code(user, election, plain_code, expires_at)
        phone = (user.phone_number or "").strip()
        if not phone:
            logger.warning("SVT SMS skipped — no phone on file for user %s", user.uuid)
            return
        try:
            from apps.notifications.services.communication_service import communication_service

            communication_service.dispatch_multi(
                template_code="svt_issued",
                channels=["sms"],
                recipient=phone,
                context={
                    "first_name": user.first_name or "Student",
                    "election_name": election.title,
                    "svt": plain_code,
                    "expiry_time": expires_at.strftime("%H:%M"),
                },
                user=user,
            )
        except Exception:
            logger.exception("Failed to send SVT SMS for user %s", user.uuid)

    def _build_public_issue_response(
        self,
        svt: SVTToken,
        election,
        *,
        message: str,
        resend_available_at=None,
    ) -> dict:
        return {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "issued_at": svt.issued_at,
            "expires_at": svt.expires_at,
            "status": svt.status,
            "masked_phone": mask_phone_number(svt.user.phone_number),
            "resend_available_at": resend_available_at,
            "validation_attempts_remaining": max(
                0,
                int(getattr(settings, "SVT_MAX_VALIDATION_ATTEMPTS", 5)) - svt.validation_attempts,
            ),
            "message": message,
        }

    def get_voting_access_status(self, election_uuid, user) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        active = self.svt_repository.get_active_svt_for_user_election(user, election)
        resend_at = None
        if active and active.status == SVTToken.Status.ISSUED and active.last_resent_at:
            cooldown = int(getattr(settings, "SVT_RESEND_COOLDOWN_SECONDS", 60))
            resend_at = active.last_resent_at + timedelta(seconds=cooldown)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "has_submitted_ballot": self._user_has_submitted_ballot(user, election),
            "svt_status": active.status if active else None,
            "expires_at": active.expires_at if active else None,
            "validated_at": active.validated_at if active else None,
            "can_request_svt": active is None and not self._user_has_submitted_ballot(user, election),
            "masked_phone": mask_phone_number(user.phone_number),
            "resend_available_at": resend_at,
            "validation_attempts_remaining": max(
                0,
                int(getattr(settings, "SVT_MAX_VALIDATION_ATTEMPTS", 5))
                - (active.validation_attempts if active else 0),
            ),
        }

    @transaction.atomic
    def request_svt(
        self,
        election_uuid,
        user,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_election_open_for_svt(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="election_not_open") from exc

        if not self.eligibility_repository.is_user_eligible(election, user):
            raise PermissionDeniedError(
                message="You are not eligible to vote in this election.",
                code="not_eligible",
            )

        if self._user_has_submitted_ballot(user, election):
            raise ConflictError(
                message="You have already voted in this election.",
                code="already_voted",
            )

        if self.svt_repository.has_active_svt_for_user_election(user, election):
            active = self.svt_repository.get_active_svt_for_user_election(user, election)
            resend_at = None
            if active and active.last_resent_at:
                cooldown = int(getattr(settings, "SVT_RESEND_COOLDOWN_SECONDS", 60))
                resend_at = active.last_resent_at + timedelta(seconds=cooldown)
            return {
                **self._build_public_issue_response(
                    active,
                    election,
                    message="A voting token has already been sent to your phone.",
                    resend_available_at=resend_at,
                ),
                "token_code": None,
            }

        plain_code = SVTToken.generate_token_code()
        expiry_minutes = int(getattr(settings, "SVT_EXPIRY_MINUTES", 10))
        now = timezone.now()
        expires_at = now + timedelta(minutes=expiry_minutes)

        svt = self.svt_repository.create(
            user=user,
            election=election,
            token_code=SVTToken.hash_token_code(plain_code),
            issued_at=now,
            expires_at=expires_at,
            status=SVTToken.Status.ISSUED,
        )

        self.audit_service.log_issued(user, svt, ip_address, user_agent)
        self._send_svt_sms(user, election, plain_code, expires_at)
        logger.info("SVT issued: %s for user %s", svt.svt_id, user.uuid)

        result = {
            **self._build_public_issue_response(
                svt,
                election,
                message="A Secure Voting Token has been sent to your registered phone number.",
            ),
            "token_code": plain_code,
        }
        self._broadcast_svt_issued(svt, user)
        return result

    @transaction.atomic
    def resend_svt(
        self,
        election_uuid,
        user,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_election_open_for_svt(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="election_not_open") from exc

        if self._user_has_submitted_ballot(user, election):
            raise ConflictError(message="You have already voted in this election.", code="already_voted")

        active = self.svt_repository.get_active_svt_for_user_election(user, election)
        if not active or active.status != SVTToken.Status.ISSUED:
            raise ConflictError(
                message="No pending voting token to resend.",
                code="svt_not_pending",
            )

        cooldown = int(getattr(settings, "SVT_RESEND_COOLDOWN_SECONDS", 60))
        if active.last_resent_at:
            next_allowed = active.last_resent_at + timedelta(seconds=cooldown)
            if timezone.now() < next_allowed:
                raise ConflictError(
                    message="Please wait before requesting another token.",
                    code="svt_resend_cooldown",
                )

        self.svt_repository.update(active, status=SVTToken.Status.REVOKED)
        issued = self.request_svt(
            election_uuid=election_uuid,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        new_svt = self.svt_repository.get_by_svt_id(issued["svt_id"])
        if new_svt:
            self.svt_repository.update(new_svt, last_resent_at=timezone.now())
            issued["resend_available_at"] = timezone.now() + timedelta(seconds=cooldown)
        issued.pop("token_code", None)
        return issued

    @transaction.atomic
    def start_voting_session(
        self,
        election_uuid,
        user,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        """Issue and validate an SVT when web voting begins — token never returned to client."""
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        active = self.svt_repository.get_active_svt_for_user_election(user, election)
        if active and active.status == SVTToken.Status.VALIDATED:
            return {
                "svt_id": str(active.svt_id),
                "election_uuid": str(election.uuid),
                "election_title": election.title,
                "status": active.status,
                "expires_at": active.expires_at,
                "validated_at": active.validated_at,
                "message": "Ballot session active.",
                "token_code": None,
            }

        if active and active.status == SVTToken.Status.ISSUED:
            self.svt_repository.update(active, status=SVTToken.Status.REVOKED)

        issued = self.request_svt(
            election_uuid=election_uuid,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        plain_code = issued["token_code"]
        session = self.validate_and_start_ballot(
            token_code=plain_code,
            user=user,
            election_uuid=election_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session["token_code"] = plain_code
        return session

    def _broadcast_svt_issued(self, svt, user) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.svt_issued(
                svt=svt,
                user=user,
                admin_stats=dashboard_service.get_admin_overview(),
            )
        except Exception:
            logger.exception("Failed to broadcast SVT issued event for %s", svt.svt_id)

    def _broadcast_svt_validated(self, svt, user) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.svt_validated(
                svt=svt,
                user=user,
                student_stats=dashboard_service.get_student_overview(user),
            )
        except Exception:
            logger.exception("Failed to broadcast SVT validated event for %s", svt.svt_id)

    def _broadcast_svt_consumed(self, svt, user, vote_count: int) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.svt_consumed(
                svt=svt,
                user=user,
                vote_count=vote_count,
                admin_stats=dashboard_service.get_admin_overview(),
                student_stats=dashboard_service.get_student_overview(user),
            )
        except Exception:
            logger.exception("Failed to broadcast SVT consumed event for %s", svt.svt_id)

    @transaction.atomic
    def validate_and_start_ballot(
        self,
        token_code: str,
        user,
        election_uuid,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        normalized = str(token_code or "").strip()
        from core.utils.svt_token_format import is_valid_svt_format, normalize_svt_token

        demo_code = match_dev_demo_svt_code(normalized)
        if demo_code:
            svt = self._get_or_create_demo_svt(user, election, demo_code)
        else:
            if not is_valid_svt_format(normalized):
                self._record_failed_validation_attempt(user, election)
                raise ValidationError(
                    message="Invalid Secure Voting Token. Please check the code sent to your phone.",
                    code="svt_invalid",
                )

            canonical = normalize_svt_token(normalized)
            svt = self.svt_repository.get_by_token_code(canonical)
            if not svt:
                self._record_failed_validation_attempt(user, election)
                raise NotFoundError(message="Invalid voting token.", code="svt_not_found")

        if svt.status == SVTToken.Status.VALIDATED:
            try:
                if svt.user_id != user.id:
                    raise DjangoValidationError("This voting token does not belong to you.")
                if svt.election_id != election.id:
                    raise DjangoValidationError("This voting token does not belong to this election.")
                from apps.security.validators import (
                    _check_ballot_session_active,
                    _check_svt_not_expired_or_revoked,
                )

                _check_svt_not_expired_or_revoked(svt)
                _check_ballot_session_active(svt)
            except DjangoValidationError as exc:
                raise ValidationError(message=str(exc), code="svt_invalid") from exc

            session_minutes = int(getattr(settings, "BALLOT_SESSION_MINUTES", 15))
            return {
                "svt_id": str(svt.svt_id),
                "election_uuid": str(election.uuid),
                "election_title": election.title,
                "status": svt.status,
                "expires_at": svt.expires_at,
                "validated_at": svt.validated_at,
                "session_expires_at": (svt.validated_at or timezone.now())
                + timedelta(minutes=session_minutes),
                "message": "Ballot session active. Continue your selections and submit your ballot.",
            }

        try:
            validate_svt_for_ballot_start(svt, user, election)
        except DjangoValidationError as exc:
            self._record_failed_validation_attempt(user, election, svt=svt)
            raise ValidationError(message=str(exc), code="svt_invalid") from exc

        now = timezone.now()
        svt = self.svt_repository.update(
            svt,
            status=SVTToken.Status.VALIDATED,
            validated_at=now,
            validation_attempts=0,
        )

        self.audit_service.log_validated(user, svt, ip_address, user_agent)
        self.audit_service.log_ballot_started(user, svt, ip_address, user_agent)
        logger.info("SVT validated for ballot: %s user %s", svt.svt_id, user.uuid)

        self._broadcast_svt_validated(svt, user)

        session_minutes = int(getattr(settings, "BALLOT_SESSION_MINUTES", 15))
        return {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "status": svt.status,
            "expires_at": svt.expires_at,
            "validated_at": svt.validated_at,
            "session_expires_at": now + timedelta(minutes=session_minutes),
            "message": "Ballot session started. Complete your selections and submit your ballot.",
        }

    def _demo_svt_student_user(self, user) -> bool:
        role_name = getattr(getattr(user, "role", None), "name", None)
        return role_name == Role.Name.STUDENT

    def _assert_demo_svt_request_allowed(self, user, election, demo_code: str) -> None:
        if not demo_svt_enabled():
            raise ValidationError(
                message="Demo voting codes are not enabled.",
                code="demo_svt_disabled",
            )
        if not self._demo_svt_student_user(user):
            raise PermissionDeniedError(
                message="Demo voting codes are only available to student accounts.",
                code="demo_svt_student_only",
            )
        try:
            validate_election_open_for_svt(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="election_not_open") from exc

        if not self.eligibility_repository.is_user_eligible(election, user):
            raise PermissionDeniedError(
                message="You are not eligible to vote in this election.",
                code="not_eligible",
            )

        if self._user_has_submitted_ballot(user, election):
            raise ConflictError(
                message="You have already voted in this election.",
                code="already_voted",
            )

        used_elsewhere = self.svt_repository.get_queryset().filter(
            user=user,
            source_demo_code=demo_code,
            status=SVTToken.Status.USED,
        ).exclude(election=election)
        if used_elsewhere.exists():
            raise ValidationError(
                message=(
                    "This demo voting code was already used in another election. "
                    "Choose a different code from the demo pool."
                ),
                code="demo_svt_election_bound",
            )

        active_elsewhere = (
            self.svt_repository.get_queryset()
            .filter(
                user=user,
                source_demo_code=demo_code,
                status__in=[SVTToken.Status.ISSUED, SVTToken.Status.VALIDATED],
            )
            .exclude(election=election)
            .first()
        )
        if active_elsewhere:
            raise ValidationError(
                message=(
                    "This demo voting code is active in another election. "
                    "Finish or abandon that ballot before reusing the code."
                ),
                code="demo_svt_active_elsewhere",
            )

    def _demo_svt_expires_at(self):
        return datetime(
            DEMO_SVT_FAR_FUTURE_YEAR,
            12,
            31,
            23,
            59,
            59,
            tzinfo=timezone.utc,
        )

    def _get_or_create_demo_svt(self, user, election, demo_code: str) -> SVTToken:
        self._assert_demo_svt_request_allowed(user, election, demo_code)

        token_hash = SVTToken.hash_demo_token_code(demo_code, user.pk, election.pk)
        existing = self.svt_repository.get_by_token_hash(token_hash)
        if existing:
            if existing.status == SVTToken.Status.USED:
                raise ConflictError(
                    message="You have already voted in this election with this demo code.",
                    code="already_voted",
                )
            return existing

        pending_sms = (
            self.svt_repository.get_queryset()
            .filter(
                user=user,
                election=election,
                status=SVTToken.Status.ISSUED,
                source_demo_code="",
            )
            .order_by("-issued_at")
            .first()
        )
        if pending_sms and not pending_sms.source_demo_code:
            self.svt_repository.update(pending_sms, status=SVTToken.Status.REVOKED)

        now = timezone.now()
        return self.svt_repository.create(
            user=user,
            election=election,
            token_code=token_hash,
            source_demo_code=demo_code,
            issued_at=now,
            expires_at=self._demo_svt_expires_at(),
            status=SVTToken.Status.ISSUED,
        )

    def _record_failed_validation_attempt(self, user, election, svt: SVTToken | None = None) -> None:
        max_attempts = int(getattr(settings, "SVT_MAX_VALIDATION_ATTEMPTS", 5))
        target = svt
        if not target:
            target = self.svt_repository.get_active_svt_for_user_election(user, election)
        if not target or target.status != SVTToken.Status.ISSUED:
            return
        attempts = target.validation_attempts + 1
        if attempts >= max_attempts:
            self.svt_repository.update(
                target,
                validation_attempts=attempts,
                status=SVTToken.Status.REVOKED,
            )
            return
        self.svt_repository.update(target, validation_attempts=attempts)

    def get_svt_for_submit(self, token_code: str, user, election_uuid) -> SVTToken:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        normalized = str(token_code or "").strip()
        demo_code = match_dev_demo_svt_code(normalized)
        if demo_code:
            token_hash = SVTToken.hash_demo_token_code(demo_code, user.pk, election.pk)
            svt = self.svt_repository.get_by_token_hash(token_hash)
            if not svt:
                raise NotFoundError(message="Invalid voting token.", code="svt_not_found")
        else:
            from core.utils.svt_token_format import normalize_svt_token

            canonical = normalize_svt_token(normalized)
            if not canonical:
                raise NotFoundError(message="Invalid voting token.", code="svt_not_found")
            svt = self.svt_repository.get_by_token_code(canonical)
            if not svt:
                raise NotFoundError(message="Invalid voting token.", code="svt_not_found")

        try:
            validate_svt_for_ballot_submit(svt, user, election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="svt_invalid") from exc

        return svt

    @transaction.atomic
    def consume_svt(
        self,
        svt: SVTToken,
        user,
        vote_count: int,
        ip_address=None,
        user_agent=None,
    ) -> SVTToken:
        svt = self.svt_repository.get_by_svt_id(svt.svt_id)
        if not svt or svt.status != SVTToken.Status.VALIDATED:
            raise ConflictError(
                message="Voting token is no longer valid for submission.",
                code="svt_already_consumed",
            )

        now = timezone.now()
        svt = self.svt_repository.update(
            svt,
            status=SVTToken.Status.USED,
            used_at=now,
        )

        self.audit_service.log_ballot_submitted(user, svt, vote_count, ip_address, user_agent)
        self.audit_service.log_consumed(user, svt, vote_count, ip_address, user_agent)
        self._broadcast_svt_consumed(svt, user, vote_count)
        return svt

    def verify_vote_by_svt(
        self,
        token_code: str,
        user,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        svt = self.svt_repository.get_by_token_code(token_code)
        if not svt:
            raise NotFoundError(message="Invalid voting token.", code="svt_not_found")

        try:
            validate_svt_for_verification(svt, user)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="svt_invalid") from exc

        if svt.status != SVTToken.Status.USED:
            raise ValidationError(
                message="No ballot has been submitted with this token yet.",
                code="svt_not_used",
            )

        votes = list(self.vote_repository.list_by_svt_id(svt.svt_id))
        if not votes:
            raise NotFoundError(message="No votes found for this token.", code="vote_not_found")

        all_valid = True
        positions_completed = []
        for vote in votes:
            expected_hash = Vote.compute_vote_hash(
                election_id=vote.election_id,
                position_id=vote.position_id,
                candidate_id=vote.candidate_id,
                user_id=vote.user_id,
                channel_id=vote.channel_id,
                timestamp_iso=vote.timestamp.isoformat(),
            )
            if vote.vote_hash != expected_hash:
                all_valid = False
            if vote.position.title not in positions_completed:
                positions_completed.append(vote.position.title)

        self.audit_service.log_verified(user, svt, ip_address, user_agent)

        first_vote = votes[0]
        return {
            "is_valid": all_valid,
            "election_uuid": str(first_vote.election.uuid),
            "election_title": first_vote.election.title,
            "positions_completed": positions_completed,
            "positions_count": len(positions_completed),
            "votes_count": len(votes),
            "timestamp": votes[-1].timestamp,
            "svt_status": svt.status,
            "used_at": svt.used_at,
        }

    def get_ballot_confirmation_by_svt(self, token_code: str, user) -> dict:
        svt = self.svt_repository.get_by_token_code(token_code)
        if not svt:
            raise NotFoundError(message="Invalid voting token.", code="svt_not_found")

        if svt.user_id != user.id:
            raise PermissionDeniedError(
                message="This voting token does not belong to you.",
                code="svt_access_denied",
            )

        if svt.status != SVTToken.Status.USED:
            raise ValidationError(
                message="This token has not been used to submit a ballot yet.",
                code="svt_not_used",
            )

        votes = list(self.vote_repository.list_by_svt_id(svt.svt_id))
        if not votes:
            raise NotFoundError(message="No votes found for this token.", code="vote_not_found")

        positions_completed = []
        seen_positions = set()
        for vote in votes:
            if vote.position_id not in seen_positions:
                seen_positions.add(vote.position_id)
                positions_completed.append(vote.position.title)

        first_vote = votes[0]
        return {
            "election_uuid": str(first_vote.election.uuid),
            "election_title": first_vote.election.title,
            "positions_completed": positions_completed,
            "positions_count": len(positions_completed),
            "timestamp": votes[-1].timestamp,
            "svt_status": svt.status,
            "used_at": svt.used_at,
            "message": "Your vote has been recorded successfully.",
        }

    def list_for_election(self, election_uuid, status: str | None = None):
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        return self.svt_repository.list_for_election(election, status=status)

    @transaction.atomic
    def revoke_svt(self, svt_id, admin_user, ip_address=None, user_agent=None) -> SVTToken:
        svt = self.svt_repository.get_by_svt_id(svt_id)
        if not svt:
            raise NotFoundError(message="SVT not found.", code="svt_not_found")

        if svt.status == SVTToken.Status.USED:
            raise ConflictError(
                message="Cannot revoke a token that has already been used.",
                code="svt_already_used",
            )

        if svt.status == SVTToken.Status.REVOKED:
            raise ConflictError(message="Token is already revoked.", code="svt_already_revoked")

        svt = self.svt_repository.update(svt, status=SVTToken.Status.REVOKED)
        self.audit_service.log_revoked(admin_user, svt, ip_address, user_agent)
        return svt

    @transaction.atomic
    def reissue_svt(
        self,
        svt_id,
        admin_user,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        old_svt = self.svt_repository.get_by_svt_id(svt_id)
        if not old_svt:
            raise NotFoundError(message="SVT not found.", code="svt_not_found")

        if old_svt.status == SVTToken.Status.USED:
            raise ConflictError(
                message="Cannot reissue a token that has already been used.",
                code="svt_already_used",
            )

        self.svt_repository.update(old_svt, status=SVTToken.Status.REVOKED)

        plain_code = SVTToken.generate_token_code()
        expiry_minutes = int(getattr(settings, "SVT_EXPIRY_MINUTES", 30))
        now = timezone.now()
        expires_at = now + timedelta(minutes=expiry_minutes)

        new_svt = self.svt_repository.create(
            user=old_svt.user,
            election=old_svt.election,
            token_code=SVTToken.hash_token_code(plain_code),
            issued_at=now,
            expires_at=expires_at,
            status=SVTToken.Status.ISSUED,
        )

        self.audit_service.log_reissued(admin_user, old_svt, new_svt, ip_address, user_agent)
        self._log_dev_svt_code(old_svt.user, old_svt.election, plain_code, expires_at)

        return {
            "svt_id": str(new_svt.svt_id),
            "token_code": plain_code,
            "election_uuid": str(new_svt.election.uuid),
            "user_uuid": str(new_svt.user.uuid),
            "user_email": new_svt.user.email,
            "issued_at": new_svt.issued_at,
            "expires_at": new_svt.expires_at,
            "status": new_svt.status,
            "replaced_svt_id": str(old_svt.svt_id),
        }


svt_service = SVTService()
