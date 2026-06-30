import logging

from django.utils import timezone

from apps.elections.models import Election
from apps.strongroom.models import VaultAccessRequest
from apps.strongroom.repositories.vault_repository import VaultAccessRequestRepository
from apps.strongroom.services.custody_service import custody_service
from core.exceptions import PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

VAULT_ELIGIBLE_STATUSES = {Election.Status.CLOSED, Election.Status.ARCHIVED}


class VaultAccessService:
    def __init__(self, repository: VaultAccessRequestRepository | None = None):
        self.repository = repository or VaultAccessRequestRepository()

    def list_requests(self, election) -> list[dict]:
        return [self._serialize(item) for item in self.repository.list_for_election(election)]

    def create_request(
        self,
        election,
        *,
        actor,
        reason: str,
        justification: str = "",
    ) -> dict:
        self._ensure_vault_eligible(election)
        if reason not in dict(VaultAccessRequest.Reason.choices):
            raise ValidationError(message="Invalid access reason.", code="invalid_reason")

        access_request = self.repository.create(
            election=election,
            requested_by=actor,
            reason=reason,
            justification=justification.strip(),
            status=VaultAccessRequest.Status.PENDING,
        )
        custody_service.record(
            election=election,
            action="vault_access_requested",
            actor=actor,
            entity_type="vault_access_request",
            entity_uuid=access_request.uuid,
            previous_state={},
            current_state={"status": access_request.status, "reason": reason},
            metadata={"justification": justification.strip()},
        )
        return self._serialize(access_request)

    def approve_request(self, access_request: VaultAccessRequest, *, actor) -> dict:
        if access_request.status != VaultAccessRequest.Status.PENDING:
            raise ValidationError(message="Request is not pending.", code="invalid_status")
        self._ensure_vault_eligible(access_request.election)

        now = timezone.now()
        self.repository.save(
            access_request,
            status=VaultAccessRequest.Status.APPROVED,
            reviewed_by=actor,
            reviewed_at=now,
        )
        custody_service.record(
            election=access_request.election,
            action="vault_access_approved",
            actor=actor,
            entity_type="vault_access_request",
            entity_uuid=access_request.uuid,
            previous_state={"status": VaultAccessRequest.Status.PENDING},
            current_state={"status": access_request.status, "reviewed_at": now.isoformat()},
            metadata={"reason": access_request.reason},
        )
        return self._serialize(access_request)

    def deny_request(self, access_request: VaultAccessRequest, *, actor) -> dict:
        if access_request.status != VaultAccessRequest.Status.PENDING:
            raise ValidationError(message="Request is not pending.", code="invalid_status")

        now = timezone.now()
        self.repository.save(
            access_request,
            status=VaultAccessRequest.Status.DENIED,
            reviewed_by=actor,
            reviewed_at=now,
        )
        custody_service.record(
            election=access_request.election,
            action="vault_access_denied",
            actor=actor,
            entity_type="vault_access_request",
            entity_uuid=access_request.uuid,
            previous_state={"status": VaultAccessRequest.Status.PENDING},
            current_state={"status": access_request.status},
            metadata={"reason": access_request.reason},
        )
        return self._serialize(access_request)

    def get_request(self, request_uuid) -> VaultAccessRequest | None:
        return self.repository.get_by_uuid(request_uuid)

    def _ensure_vault_eligible(self, election) -> None:
        if election.status not in VAULT_ELIGIBLE_STATUSES:
            raise PermissionDeniedError(
                message="Vault access is only available for completed elections.",
                code="election_not_completed",
            )

    def _serialize(self, access_request: VaultAccessRequest) -> dict:
        return {
            "uuid": str(access_request.uuid),
            "election_uuid": str(access_request.election.uuid),
            "reason": access_request.reason,
            "reason_label": access_request.get_reason_display(),
            "justification": access_request.justification,
            "status": access_request.status,
            "requested_by": access_request.requested_by.get_full_name(),
            "reviewed_by": access_request.reviewed_by.get_full_name() if access_request.reviewed_by else None,
            "reviewed_at": access_request.reviewed_at,
            "created_at": access_request.created_at,
        }


vault_access_service = VaultAccessService()
