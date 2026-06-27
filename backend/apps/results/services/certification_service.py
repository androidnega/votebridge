import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.elections.repositories.election_repository import ElectionRepository
from apps.results.models import ElectionResult
from apps.results.repositories.election_result_repository import ElectionResultRepository
from apps.results.services.results_service import result_integrity_service
from apps.results.validators import validate_result_status_transition
from apps.security.models import AuditLog
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class CertificationService:
    """Certify, publish, and archive election results."""

    def __init__(
        self,
        result_repository: ElectionResultRepository | None = None,
        election_repository: ElectionRepository | None = None,
    ):
        self.result_repository = result_repository or ElectionResultRepository()
        self.election_repository = election_repository or ElectionRepository()

    def get_result_for_election(self, election_uuid) -> ElectionResult:
        result = self.result_repository.get_by_election_uuid(election_uuid)
        if not result:
            raise NotFoundError(message="Results not found for this election.", code="result_not_found")
        return result

    @transaction.atomic
    def certify(
        self,
        election_uuid,
        super_admin,
        *,
        notes: str = "",
        acknowledge_fraud: bool = False,
        fraud_notes: str = "",
    ) -> ElectionResult:
        result = self.get_result_for_election(election_uuid)
        try:
            validate_result_status_transition(result.status, ElectionResult.Status.CERTIFIED)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_result_transition") from exc

        integrity = result_integrity_service.verify(
            result.election,
            fraud_acknowledged=acknowledge_fraud,
        )
        if not integrity["is_valid"]:
            raise ValidationError(
                message="Integrity verification failed: " + "; ".join(integrity["blocking_issues"]),
                code="integrity_failed",
            )

        result = self.result_repository.update(
            result,
            status=ElectionResult.Status.CERTIFIED,
            integrity_report=integrity,
            certified_at=timezone.now(),
            certified_by=super_admin,
            certification_notes=notes.strip(),
            fraud_acknowledged=acknowledge_fraud,
            fraud_acknowledgment_notes=fraud_notes.strip() if acknowledge_fraud else "",
        )
        self._log_audit(super_admin, result.election, "results_certified")
        self._broadcast_certified(result)
        return result

    @transaction.atomic
    def publish(self, election_uuid, super_admin) -> ElectionResult:
        result = self.get_result_for_election(election_uuid)
        try:
            validate_result_status_transition(result.status, ElectionResult.Status.PUBLISHED)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_result_transition") from exc

        result = self.result_repository.update(
            result,
            status=ElectionResult.Status.PUBLISHED,
            published_at=timezone.now(),
            published_by=super_admin,
        )
        self._log_audit(super_admin, result.election, "results_published")
        self._broadcast_published(result)
        return result

    @transaction.atomic
    def archive(self, election_uuid, super_admin) -> ElectionResult:
        result = self.get_result_for_election(election_uuid)
        try:
            validate_result_status_transition(result.status, ElectionResult.Status.ARCHIVED)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_result_transition") from exc

        result = self.result_repository.update(
            result,
            status=ElectionResult.Status.ARCHIVED,
            archived_at=timezone.now(),
            archived_by=super_admin,
        )
        self._log_audit(super_admin, result.election, "results_archived")
        return result

    def _log_audit(self, user, election, action: str) -> None:
        AuditLog.objects.create(
            user=user,
            election=election,
            event_type=AuditLog.EventType.ADMIN_ACTION,
            metadata={"action": action},
        )

    def _broadcast_certified(self, result: ElectionResult) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.results_certified(result)
        except Exception:
            logger.exception("Failed to broadcast results_certified for %s", result.uuid)

    def _broadcast_published(self, result: ElectionResult) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.results_published(result)
        except Exception:
            logger.exception("Failed to broadcast results_published for %s", result.uuid)


certification_service = CertificationService()
