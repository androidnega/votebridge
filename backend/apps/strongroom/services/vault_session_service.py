import logging
from datetime import timedelta

from django.utils import timezone

from apps.accounts.repositories.user_repository import UserRepository
from apps.strongroom.models import StrongroomCommittee, VaultAccessRequest, VaultSession
from apps.strongroom.repositories.vault_repository import (
    StrongroomCommitteeRepository,
    VaultAccessRequestRepository,
    VaultSessionRepository,
)
from apps.strongroom.services.custody_service import custody_service
from apps.strongroom.services.integrity_verification_service import integrity_verification_service
from core.exceptions import AuthenticationError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

INVALID_CREDENTIALS = "Access denied."


class VaultSessionService:
    def __init__(
        self,
        session_repository: VaultSessionRepository | None = None,
        access_repository: VaultAccessRequestRepository | None = None,
        committee_repository: StrongroomCommitteeRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.session_repository = session_repository or VaultSessionRepository()
        self.access_repository = access_repository or VaultAccessRequestRepository()
        self.committee_repository = committee_repository or StrongroomCommitteeRepository()
        self.user_repository = user_repository or UserRepository()

    def start_session(self, access_request: VaultAccessRequest, *, actor) -> dict:
        self._validate_access_request(access_request)
        committee = self._approved_committee(access_request.election)

        existing = self.session_repository.get_active_for_election(access_request.election)
        if existing:
            raise ValidationError(
                message="An active vault session already exists for this election.",
                code="session_exists",
            )

        session = self.session_repository.create(
            election=access_request.election,
            access_request=access_request,
            initiated_by=actor,
            status=VaultSession.Status.AWAITING_CUSTODIANS,
            session_duration_hours=committee.session_duration_hours,
            authenticated_custodians=[],
        )
        self.access_repository.save(access_request, status=VaultAccessRequest.Status.CONSUMED)

        custody_service.record(
            election=access_request.election,
            action="vault_session_initiated",
            actor=actor,
            entity_type="vault_session",
            entity_uuid=session.uuid,
            previous_state={},
            current_state={"status": session.status},
            metadata={
                "access_reason": access_request.reason,
                "required_custodians": committee.members.count(),
            },
        )
        return self._serialize(session, committee)

    def authenticate_custodian(
        self,
        session: VaultSession,
        *,
        identifier: str,
        password: str,
        ip_address: str | None = None,
    ) -> dict:
        session = self._refresh_session(session)
        if session.status != VaultSession.Status.AWAITING_CUSTODIANS:
            raise ValidationError(message="Session is not awaiting custodians.", code="invalid_status")

        committee = self._approved_committee(session.election)
        user = self._resolve_user(identifier)
        if not user or not user.check_password(password):
            custody_service.record(
                election=session.election,
                action="vault_access_denied",
                actor=user,
                entity_type="vault_session",
                entity_uuid=session.uuid,
                previous_state={"status": session.status},
                current_state={"status": session.status},
                metadata={"identifier": identifier, "ip_address": ip_address},
            )
            raise AuthenticationError(message=INVALID_CREDENTIALS, code="access_denied")

        member = committee.members.filter(user=user).first()
        if not member:
            custody_service.record(
                election=session.election,
                action="vault_access_denied",
                actor=user,
                entity_type="vault_session",
                entity_uuid=session.uuid,
                previous_state={"status": session.status},
                current_state={"status": session.status},
                metadata={"reason": "not_committee_member"},
            )
            raise AuthenticationError(message=INVALID_CREDENTIALS, code="access_denied")

        authenticated = list(session.authenticated_custodians or [])
        if any(entry.get("user_uuid") == str(user.uuid) for entry in authenticated):
            raise ValidationError(message="Custodian already authenticated.", code="already_authenticated")

        expected_order = len(authenticated) + 1
        if member.custodian_order != expected_order:
            custody_service.record(
                election=session.election,
                action="vault_access_denied",
                actor=user,
                entity_type="vault_session",
                entity_uuid=session.uuid,
                previous_state={"status": session.status},
                current_state={"status": session.status},
                metadata={"reason": "out_of_order", "expected_order": expected_order},
            )
            raise AuthenticationError(message=INVALID_CREDENTIALS, code="access_denied")

        now = timezone.now()
        authenticated.append(
            {
                "user_uuid": str(user.uuid),
                "full_name": user.get_full_name(),
                "custodian_order": member.custodian_order,
                "authenticated_at": now.isoformat(),
            }
        )
        session.authenticated_custodians = authenticated

        required = committee.members.count()
        if len(authenticated) >= required:
            expires_at = now + timedelta(hours=session.session_duration_hours)
            self.session_repository.save(
                session,
                status=VaultSession.Status.ACTIVE,
                opened_at=now,
                expires_at=expires_at,
                authenticated_custodians=authenticated,
            )
            custody_service.record(
                election=session.election,
                action="vault_opened",
                actor=user,
                entity_type="vault_session",
                entity_uuid=session.uuid,
                previous_state={"status": VaultSession.Status.AWAITING_CUSTODIANS},
                current_state={
                    "status": VaultSession.Status.ACTIVE,
                    "opened_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                },
                metadata={
                    "custodians": [entry["full_name"] for entry in authenticated],
                    "access_reason": session.access_request.reason,
                },
            )
        else:
            self.session_repository.save(session, authenticated_custodians=authenticated)
            custody_service.record(
                election=session.election,
                action="vault_custodian_verified",
                actor=user,
                entity_type="vault_session",
                entity_uuid=session.uuid,
                previous_state={"authenticated_count": len(authenticated) - 1},
                current_state={"authenticated_count": len(authenticated)},
                metadata={"custodian_order": member.custodian_order},
            )

        session.refresh_from_db()
        return self._serialize(session, committee)

    def get_session(self, session_uuid, *, actor=None) -> dict:
        session = self.session_repository.get_by_uuid(session_uuid)
        if not session:
            raise ValidationError(message="Vault session not found.", code="not_found")
        session = self._expire_if_needed(session)
        committee = self.committee_repository.get_by_election(session.election)
        payload = self._serialize(session, committee)
        if session.status == VaultSession.Status.ACTIVE:
            payload["evidence"] = self._evidence_package(session)
        return payload

    def close_session(self, session: VaultSession, *, actor, reason: str = "manual_close") -> dict:
        session = self._refresh_session(session)
        if session.status not in {VaultSession.Status.ACTIVE, VaultSession.Status.AWAITING_CUSTODIANS}:
            raise ValidationError(message="Session cannot be closed.", code="invalid_status")
        return self._close_and_reseal(session, actor=actor, reason=reason)

    def _expire_if_needed(self, session: VaultSession) -> VaultSession:
        if session.status != VaultSession.Status.ACTIVE or not session.expires_at:
            return session
        if timezone.now() < session.expires_at:
            return session
        return self._close_and_reseal(session, actor=None, reason="session_timeout")

    def _close_and_reseal(self, session: VaultSession, *, actor, reason: str) -> VaultSession:
        now = timezone.now()
        previous_status = session.status
        self.session_repository.save(
            session,
            status=VaultSession.Status.RESEALED,
            closed_at=now,
        )
        custody_service.record(
            election=session.election,
            action="vault_resealed",
            actor=actor,
            entity_type="vault_session",
            entity_uuid=session.uuid,
            previous_state={"status": previous_status},
            current_state={"status": VaultSession.Status.RESEALED, "closed_at": now.isoformat()},
            metadata={
                "reason": reason,
                "session_duration_hours": session.session_duration_hours,
                "custodians": session.authenticated_custodians,
            },
        )
        session.refresh_from_db()
        return session

    def _evidence_package(self, session: VaultSession) -> dict:
        dashboard = integrity_verification_service.get_dashboard(session.election.uuid)
        return {
            "election_overview": {
                "title": dashboard.get("election_title"),
                "status": dashboard.get("election_status"),
                "seal_status": dashboard.get("seal_status"),
            },
            "integrity_summary": {
                "integrity_score": dashboard.get("integrity_score"),
                "ballot_seals_count": dashboard.get("ballot_seals_count"),
                "verification_hash": dashboard.get("verification_hash"),
            },
            "certification_summary": dashboard.get("certification_summary") or {},
            "chain_of_custody": dashboard.get("custody_timeline") or [],
            "audit_summary": dashboard.get("audit_summary") or {},
            "investigation_outcomes": dashboard.get("investigation_outcomes") or [],
            "evidence_export": {
                "available": True,
                "formats": ["json"],
                "session_uuid": str(session.uuid),
            },
        }

    def _validate_access_request(self, access_request: VaultAccessRequest) -> None:
        if access_request.status != VaultAccessRequest.Status.APPROVED:
            raise PermissionDeniedError(
                message="Access request must be approved before opening the vault.",
                code="access_not_approved",
            )

    def _approved_committee(self, election) -> StrongroomCommittee:
        committee = self.committee_repository.get_by_election(election)
        if not committee or committee.status not in {
            StrongroomCommittee.Status.APPROVED,
            StrongroomCommittee.Status.LOCKED,
        }:
            raise PermissionDeniedError(
                message="Strong room committee is not approved.",
                code="committee_not_approved",
            )
        if committee.members.count() < 2:
            raise ValidationError(message="Committee requires at least two custodians.", code="invalid_committee")
        return committee

    def _resolve_user(self, identifier: str):
        raw = (identifier or "").strip()
        if not raw:
            return None
        if "@" in raw:
            return self.user_repository.get_by_email(raw)
        if "/" in raw:
            return self.user_repository.get_by_index_number(raw)
        user = self.user_repository.get_by_username(raw)
        return user or self.user_repository.get_by_index_number(raw)

    def _refresh_session(self, session: VaultSession) -> VaultSession:
        return self._expire_if_needed(session)

    def _serialize(self, session: VaultSession, committee: StrongroomCommittee | None) -> dict:
        required = committee.members.count() if committee else 0
        authenticated = session.authenticated_custodians or []
        next_order = len(authenticated) + 1 if session.status == VaultSession.Status.AWAITING_CUSTODIANS else None
        return {
            "uuid": str(session.uuid),
            "election_uuid": str(session.election.uuid),
            "status": session.status,
            "terminal_state": self._terminal_state(session, required, next_order),
            "session_duration_hours": session.session_duration_hours,
            "authenticated_custodians": authenticated,
            "required_custodians": required,
            "next_custodian_order": next_order,
            "opened_at": session.opened_at,
            "expires_at": session.expires_at,
            "closed_at": session.closed_at,
            "access_reason": session.access_request.reason,
            "access_reason_label": session.access_request.get_reason_display(),
        }

    def _terminal_state(self, session: VaultSession, required: int, next_order: int | None) -> str:
        if session.status == VaultSession.Status.AWAITING_CUSTODIANS and next_order:
            return f"waiting_for_custodian_{next_order}"
        mapping = {
            VaultSession.Status.ACTIVE: "access_granted",
            VaultSession.Status.EXPIRED: "session_expired",
            VaultSession.Status.CLOSED: "vault_closed",
            VaultSession.Status.RESEALED: "vault_resealed",
        }
        return mapping.get(session.status, session.status)


vault_session_service = VaultSessionService()
