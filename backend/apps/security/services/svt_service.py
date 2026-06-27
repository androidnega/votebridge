import logging
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MFALog
from apps.accounts.services.mfa_service import MFAService
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
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

        self.svt_repository.revoke_issued_for_user_election(user, election)

        plain_code = SVTToken.generate_token_code()
        expiry_minutes = int(getattr(settings, "SVT_EXPIRY_MINUTES", 30))
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
        logger.info("SVT issued: %s for user %s", svt.svt_id, user.uuid)

        result = {
            "svt_id": str(svt.svt_id),
            "token_code": plain_code,
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "issued_at": svt.issued_at,
            "expires_at": svt.expires_at,
            "status": svt.status,
            "message": "Keep this token secure. Enter it once to vote across all positions on your ballot.",
        }
        self._broadcast_svt_issued(svt, user)
        return result

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

        svt = self.svt_repository.get_by_token_code(token_code)
        if not svt:
            raise NotFoundError(message="Invalid voting token.", code="svt_not_found")

        try:
            validate_svt_for_ballot_start(svt, user, election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="svt_invalid") from exc

        svt = self.svt_repository.update(svt, status=SVTToken.Status.VALIDATED)

        self.audit_service.log_validated(user, svt, ip_address, user_agent)
        self.audit_service.log_ballot_started(user, svt, ip_address, user_agent)
        logger.info("SVT validated for ballot: %s user %s", svt.svt_id, user.uuid)

        self._broadcast_svt_validated(svt, user)

        return {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "status": svt.status,
            "expires_at": svt.expires_at,
            "message": "Ballot session started. Complete your selections and submit your ballot.",
        }

    def get_svt_for_submit(self, token_code: str, user, election_uuid) -> SVTToken:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        svt = self.svt_repository.get_by_token_code(token_code)
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
