import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.accounts.repositories.user_repository import UserRepository
from apps.accounts.utils.phone import normalize_phone
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
        data: dict,
        *,
        user_uuid=None,
        index_number: str | None = None,
        verified_by=None,
    ) -> VoterEligibility:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        user = self._resolve_voter_user(user_uuid=user_uuid, index_number=index_number)
        phone_number = (data.pop("phone_number", None) or "").strip()
        if phone_number:
            self.user_repository.update(user, phone_number=normalize_phone(phone_number))

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

    def _resolve_voter_user(self, *, user_uuid=None, index_number: str | None = None):
        if user_uuid:
            user = self.user_repository.get_by_uuid(user_uuid)
            if not user:
                raise NotFoundError(message="User not found.", code="user_not_found")
            return user

        normalized = (index_number or "").strip().upper()
        if not normalized:
            raise ValidationError(
                message="Index number is required when user_uuid is not provided.",
                code="index_number_required",
            )

        user = self.user_repository.get_by_index_number(normalized)
        if not user:
            raise NotFoundError(
                message=f"No student found with index number {normalized}.",
                code="user_not_found",
            )
        return user

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

    def import_eligibility_rows(
        self,
        election_uuid,
        rows: list[dict],
        *,
        default_is_eligible: bool = True,
        default_eligibility_reason: str = "Bulk import",
        verified_by=None,
    ) -> dict:
        """Resolve uploaded rows to users and create or update eligibility records."""
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_eligibility_election_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        imported = 0
        updated = 0
        not_found: list[str] = []
        seen_users: set[int] = set()

        for row in rows:
            index_number = (row.get("index_number") or "").strip()
            email = (row.get("email") or "").strip()
            if not index_number and not email:
                continue

            user = None
            if index_number:
                user = self.user_repository.get_by_index_number(index_number)
            if not user and email:
                user = self.user_repository.get_by_email(email)

            identifier = index_number or email
            if not user:
                not_found.append(identifier)
                continue

            if user.id in seen_users:
                continue
            seen_users.add(user.id)

            is_eligible = row.get("is_eligible", default_is_eligible)
            eligibility_reason = row.get("eligibility_reason") or default_eligibility_reason

            existing = self.eligibility_repository.get_by_election_and_user(election, user)
            if existing:
                self.eligibility_repository.update(
                    existing,
                    is_eligible=is_eligible,
                    eligibility_reason=eligibility_reason,
                    verified_by=verified_by,
                    verified_at=timezone.now() if verified_by else existing.verified_at,
                )
                updated += 1
            else:
                self.eligibility_repository.create(
                    election=election,
                    user=user,
                    is_eligible=is_eligible,
                    eligibility_reason=eligibility_reason,
                    verified_by=verified_by,
                    verified_at=timezone.now() if verified_by else None,
                )
                imported += 1

        logger.info(
            "Eligibility import for election %s: %d created, %d updated, %d not found",
            election_uuid,
            imported,
            updated,
            len(not_found),
        )

        return {
            "imported": imported,
            "updated": updated,
            "processed": imported + updated,
            "not_found": not_found,
            "not_found_count": len(not_found),
            "total_rows": len(rows),
        }

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
