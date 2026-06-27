import logging

from django.core.exceptions import ValidationError as DjangoValidationError

from apps.candidates.models import Candidate
from apps.candidates.repositories.candidate_repository import CandidateRepository
from apps.candidates.validators import (
    validate_candidate_election_editable,
    validate_candidate_position,
    validate_unique_candidate_name,
)
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.position_repository import PositionRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class CandidateService:
    """Business logic for candidate management."""

    def __init__(
        self,
        candidate_repository: CandidateRepository | None = None,
        election_repository: ElectionRepository | None = None,
        position_repository: PositionRepository | None = None,
    ):
        self.candidate_repository = candidate_repository or CandidateRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.position_repository = position_repository or PositionRepository()

    def list_candidates(self, election_uuid, status: str | None = None):
        queryset = self.candidate_repository.list_for_election(election_uuid)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_candidate(self, uuid) -> Candidate:
        candidate = self.candidate_repository.get_by_uuid(uuid)
        if not candidate:
            raise NotFoundError(message="Candidate not found.", code="candidate_not_found")
        return candidate

    def create_candidate(self, election_uuid, data: dict) -> Candidate:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        position = self._resolve_position(data.pop("position_uuid", None), election)

        try:
            validate_candidate_election_editable(election)
            validate_unique_candidate_name(election, data.get("full_name", ""))
            validate_candidate_position(position, election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="candidate_validation") from exc

        candidate = self.candidate_repository.create(
            election=election,
            position=position,
            **data,
        )
        logger.info("Candidate created: %s", candidate.uuid)
        return candidate

    def update_candidate(self, uuid, data: dict) -> Candidate:
        candidate = self.get_candidate(uuid)
        election = candidate.election

        try:
            validate_candidate_election_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        if "full_name" in data:
            try:
                validate_unique_candidate_name(
                    election,
                    data["full_name"],
                    exclude_uuid=candidate.uuid,
                )
            except DjangoValidationError as exc:
                raise ValidationError(
                    message=str(exc),
                    code="duplicate_candidate_name",
                ) from exc

        if "position_uuid" in data:
            position = self._resolve_position(data.pop("position_uuid"), election)
            try:
                validate_candidate_position(position, election)
            except DjangoValidationError as exc:
                raise ValidationError(message=str(exc), code="invalid_position") from exc
            data["position"] = position

        candidate = self.candidate_repository.update(candidate, **data)
        logger.info("Candidate updated: %s", candidate.uuid)
        return candidate

    def delete_candidate(self, uuid) -> None:
        candidate = self.get_candidate(uuid)
        try:
            validate_candidate_election_editable(candidate.election)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc.message), code="election_read_only") from exc

        self.candidate_repository.delete(candidate)
        logger.info("Candidate deleted: %s", uuid)

    def approve_candidate(self, uuid) -> Candidate:
        candidate = self.get_candidate(uuid)
        try:
            validate_candidate_election_editable(candidate.election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        if candidate.status == Candidate.Status.APPROVED:
            raise ConflictError(message="Candidate is already approved.", code="already_approved")

        candidate = self.candidate_repository.update(
            candidate,
            status=Candidate.Status.APPROVED,
        )
        logger.info("Candidate approved: %s", candidate.uuid)
        return candidate

    def reject_candidate(self, uuid) -> Candidate:
        candidate = self.get_candidate(uuid)
        try:
            validate_candidate_election_editable(candidate.election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        candidate = self.candidate_repository.update(
            candidate,
            status=Candidate.Status.REJECTED,
        )
        logger.info("Candidate rejected: %s", candidate.uuid)
        return candidate

    def _resolve_position(self, position_uuid, election):
        if not position_uuid:
            raise ValidationError(
                message="Position is required for every candidate.",
                code="position_required",
            )
        position = self.position_repository.get_by_uuid(position_uuid)
        if not position:
            raise NotFoundError(message="Position not found.", code="position_not_found")
        return position
