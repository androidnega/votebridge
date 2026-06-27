import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.accounts.repositories.user_repository import UserRepository
from apps.elections.eligibility_validators import (
    validate_eligibility_election_editable,
    validate_eligibility_unique,
)
from apps.elections.models import VoterEligibility
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class VoterEligibilityService:
    """Business logic for voter eligibility management."""

    def __init__(
        self,
        eligibility_repository: VoterEligibilityRepository | None = None,
        election_repository: ElectionRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.user_repository = user_repository or UserRepository()

    def list_eligibilities(
        self,
        election_uuid,
        query: str | None = None,
        is_eligible: bool | None = None,
    ):
        return self.eligibility_repository.search(
            election_uuid=election_uuid,
            query=query,
            is_eligible=is_eligible,
        )

    def get_eligibility(self, uuid) -> VoterEligibility:
        record = self.eligibility_repository.get_by_uuid(uuid)
        if not record:
            raise NotFoundError(
                message="Voter eligibility record not found.",
                code="eligibility_not_found",
            )
        return record

    def create_eligibility(
        self,
        election_uuid,
        user_uuid,
        data: dict,
        verified_by=None,
    ) -> VoterEligibility:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        user = self.user_repository.get_by_uuid(user_uuid)
        if not user:
            raise NotFoundError(message="User not found.", code="user_not_found")

        try:
            validate_eligibility_election_editable(election)
            validate_eligibility_unique(election, user.id)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="eligibility_validation") from exc

        record = self.eligibility_repository.create(
            election=election,
            user=user,
            is_eligible=data.get("is_eligible", True),
            eligibility_reason=data.get("eligibility_reason", ""),
            verified_by=verified_by,
            verified_at=timezone.now() if verified_by else None,
        )
        logger.info("Voter eligibility created: %s", record.uuid)
        return record

    def update_eligibility(
        self,
        uuid,
        data: dict,
        verified_by=None,
    ) -> VoterEligibility:
        record = self.get_eligibility(uuid)

        try:
            validate_eligibility_election_editable(record.election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        if verified_by:
            data["verified_by"] = verified_by
            data["verified_at"] = timezone.now()

        record = self.eligibility_repository.update(record, **data)
        logger.info("Voter eligibility updated: %s", record.uuid)
        return record

    def delete_eligibility(self, uuid) -> None:
        record = self.get_eligibility(uuid)
        try:
            validate_eligibility_election_editable(record.election)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="election_read_only") from exc

        self.eligibility_repository.delete(record)
        logger.info("Voter eligibility deleted: %s", uuid)

    def bulk_set_eligibility(
        self,
        election_uuid,
        user_uuids: list,
        is_eligible: bool,
        eligibility_reason: str,
        verified_by=None,
    ) -> list[VoterEligibility]:
        """Assign or update eligibility for multiple voters."""
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_eligibility_election_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        results = []
        for user_uuid in user_uuids:
            user = self.user_repository.get_by_uuid(user_uuid)
            if not user:
                continue

            existing = self.eligibility_repository.get_by_election_and_user(
                election, user
            )
            if existing:
                record = self.eligibility_repository.update(
                    existing,
                    is_eligible=is_eligible,
                    eligibility_reason=eligibility_reason,
                    verified_by=verified_by,
                    verified_at=timezone.now() if verified_by else existing.verified_at,
                )
            else:
                record = self.eligibility_repository.create(
                    election=election,
                    user=user,
                    is_eligible=is_eligible,
                    eligibility_reason=eligibility_reason,
                    verified_by=verified_by,
                    verified_at=timezone.now() if verified_by else None,
                )
            results.append(record)

        logger.info(
            "Bulk eligibility updated for %d voters in election %s",
            len(results),
            election_uuid,
        )
        return results

    def check_voter_eligible(self, election_uuid, user) -> bool:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return False
        return self.eligibility_repository.is_user_eligible(election, user)

    def get_votable_positions(self, election_uuid, user):
        """Foundation for voting engine — positions a voter may vote on."""
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        return self.eligibility_repository.get_eligible_positions_for_user(
            election, user
        )
