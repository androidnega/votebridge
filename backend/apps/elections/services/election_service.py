import logging

from django.core.exceptions import ValidationError as DjangoValidationError

from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.validators import (
    validate_election_can_be_deleted,
    validate_election_can_be_opened,
    validate_election_dates,
    validate_election_is_editable,
    validate_status_transition,
)
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class ElectionService:
    """Business logic for election lifecycle management."""

    def __init__(self, repository: ElectionRepository | None = None):
        self.repository = repository or ElectionRepository()

    def list_elections(
        self,
        query: str | None = None,
        status: str | None = None,
        election_type: str | None = None,
    ):
        return self.repository.search(
            query=query,
            status=status,
            election_type=election_type,
        )

    def get_election(self, uuid) -> Election:
        election = self.repository.get_by_uuid(uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        return election

    def create_election(self, created_by, data: dict) -> Election:
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        try:
            validate_election_dates(start_date, end_date)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="invalid_dates") from exc

        election = self.repository.create(created_by=created_by, **data)
        logger.info("Election created: %s", election.uuid)
        return election

    def update_election(self, uuid, data: dict) -> Election:
        election = self.get_election(uuid)
        try:
            validate_election_is_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        start_date = data.get("start_date", election.start_date)
        end_date = data.get("end_date", election.end_date)
        try:
            validate_election_dates(start_date, end_date)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="invalid_dates") from exc

        election = self.repository.update(election, **data)
        logger.info("Election updated: %s", election.uuid)
        return election

    def delete_election(self, uuid) -> None:
        election = self.get_election(uuid)
        try:
            validate_election_can_be_deleted(election)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc.message), code="election_delete_denied") from exc

        self.repository.delete(election)
        logger.info("Election deleted: %s", uuid)

    def schedule_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.SCHEDULED)

    def open_election(self, uuid, *, actor=None) -> Election:
        election = self.get_election(uuid)
        from apps.elections.services.election_readiness_service import election_readiness_service

        election_readiness_service.validate_for_open(election, actor=actor)
        return self._transition(uuid, Election.Status.OPEN)

    def pause_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.PAUSED)

    def close_election(self, uuid) -> Election:
        election = self._transition(uuid, Election.Status.CLOSED)
        self._ensure_result_pending(election)
        return election

    def _ensure_result_pending(self, election) -> None:
        try:
            from apps.results.services.results_service import results_generation_service

            results_generation_service.ensure_pending_result(election)
        except Exception:
            logger.exception("Failed to create pending result for election %s", election.uuid)

    def archive_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.ARCHIVED)

    def _transition(self, uuid, new_status: str) -> Election:
        election = self.get_election(uuid)
        try:
            validate_status_transition(election.status, new_status)
        except DjangoValidationError as exc:
            raise ValidationError(
                message=str(exc.message),
                code="invalid_status_transition",
            ) from exc

        election = self.repository.update(election, status=new_status)
        logger.info("Election %s transitioned to %s", election.uuid, new_status)
        self._broadcast_status_change(election, new_status)
        return election

    def _broadcast_status_change(self, election, new_status: str) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            if new_status == Election.Status.OPEN:
                realtime_broadcast_service.election_opened(election)
                realtime_broadcast_service.dashboard_stats(
                    role="admin",
                    user_uuid=None,
                    payload=dashboard_service.get_admin_overview(),
                )
            elif new_status == Election.Status.CLOSED:
                realtime_broadcast_service.election_closed(election)
                realtime_broadcast_service.dashboard_stats(
                    role="admin",
                    user_uuid=None,
                    payload=dashboard_service.get_admin_overview(),
                )
        except Exception:
            logger.exception("Failed to broadcast election status change for %s", election.uuid)
