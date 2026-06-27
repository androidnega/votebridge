import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.elections.models import Position
from apps.elections.position_validators import (
    validate_max_votes_allowed,
    validate_position_election_editable,
    validate_unique_position_title,
)
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.position_repository import PositionRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class PositionService:
    """Business logic for election position management."""

    def __init__(
        self,
        position_repository: PositionRepository | None = None,
        election_repository: ElectionRepository | None = None,
    ):
        self.position_repository = position_repository or PositionRepository()
        self.election_repository = election_repository or ElectionRepository()

    def list_positions(
        self,
        election_uuid,
        query: str | None = None,
        is_active: bool | None = None,
    ):
        return self.position_repository.search(
            election_uuid=election_uuid,
            query=query,
            is_active=is_active,
        )

    def get_position(self, uuid) -> Position:
        position = self.position_repository.get_by_uuid(uuid)
        if not position:
            raise NotFoundError(message="Position not found.", code="position_not_found")
        return position

    def create_position(self, election_uuid, data: dict) -> Position:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_position_election_editable(election)
            validate_unique_position_title(election, data.get("title", ""))
            validate_max_votes_allowed(data.get("max_votes_allowed", 1))
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="position_validation") from exc

        position = self.position_repository.create(election=election, **data)
        logger.info("Position created: %s", position.uuid)
        return position

    def update_position(self, uuid, data: dict) -> Position:
        position = self.get_position(uuid)
        election = position.election

        try:
            validate_position_election_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        if "title" in data:
            try:
                validate_unique_position_title(
                    election,
                    data["title"],
                    exclude_uuid=position.uuid,
                )
            except DjangoValidationError as exc:
                raise ValidationError(
                    message=str(exc),
                    code="duplicate_position_title",
                ) from exc

        if "max_votes_allowed" in data:
            try:
                validate_max_votes_allowed(data["max_votes_allowed"])
            except DjangoValidationError as exc:
                raise ValidationError(message=str(exc), code="invalid_max_votes") from exc

        position = self.position_repository.update(position, **data)
        logger.info("Position updated: %s", position.uuid)
        return position

    def delete_position(self, uuid) -> None:
        position = self.get_position(uuid)
        try:
            validate_position_election_editable(position.election)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="election_read_only") from exc

        if position.candidates.exists():
            raise ConflictError(
                message="Cannot delete a position that has candidates assigned.",
                code="position_has_candidates",
            )

        self.position_repository.delete(position)
        logger.info("Position deleted: %s", uuid)
