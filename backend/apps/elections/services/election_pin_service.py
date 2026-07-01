import logging
import secrets
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from apps.elections.models import Election, ElectionVoterPin
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from core.exceptions import AuthenticationError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class ElectionPinRepository:
    def get_active_pin(self, election, user) -> ElectionVoterPin | None:
        return (
            ElectionVoterPin.objects.filter(
                election=election,
                user=user,
                is_active=True,
                expires_at__gt=timezone.now(),
            )
            .select_related("election", "user")
            .first()
        )

    def deactivate_for_election(self, election) -> int:
        return ElectionVoterPin.objects.filter(election=election, is_active=True).update(
            is_active=False
        )

    def create_pin(self, election, user, pin_hash: str, expires_at) -> ElectionVoterPin:
        return ElectionVoterPin.objects.create(
            election=election,
            user=user,
            pin_hash=pin_hash,
            expires_at=expires_at,
        )


class ElectionPinService:
    """Generate and verify per-election USSD PINs."""

    PIN_LENGTH = 6
    MAX_ATTEMPTS = 3

    def __init__(
        self,
        repository: ElectionPinRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
    ):
        self.repository = repository or ElectionPinRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()

    @transaction.atomic
    def generate_pins_for_election(self, election: Election) -> int:
        """Issue a unique PIN to every eligible voter when an election opens."""
        self.repository.deactivate_for_election(election)
        voters = self.eligibility_repository.list_eligible_users(election)
        expires_at = election.end_date or (timezone.now() + timedelta(days=7))
        created = 0
        pin_payloads = []

        for user in voters:
            plain_pin = f"{secrets.randbelow(1_000_000):06d}"
            pin_row = self.repository.create_pin(
                election=election,
                user=user,
                pin_hash=make_password(plain_pin),
                expires_at=expires_at,
            )
            pin_payloads.append((user, plain_pin, pin_row))
            created += 1

        self._dispatch_pin_notifications(election, pin_payloads)
        logger.info("Generated %s election PINs for %s", created, election.uuid)
        return created

    def verify_pin(self, election, user, pin_code: str) -> None:
        pin_row = self.repository.get_active_pin(election, user)
        if not pin_row:
            raise NotFoundError(
                message="No active election PIN found for this voter.",
                code="election_pin_not_found",
            )

        if pin_row.attempts >= pin_row.max_attempts:
            raise AuthenticationError(
                message="Maximum election PIN attempts exceeded.",
                code="election_pin_max_attempts",
            )

        if not pin_row.verify_pin(str(pin_code).strip()):
            pin_row.attempts += 1
            pin_row.save(update_fields=["attempts"])
            raise AuthenticationError(
                message="Invalid election PIN.",
                code="election_pin_invalid",
            )

    def _dispatch_pin_notifications(self, election: Election, payloads: list) -> None:
        try:
            from apps.notifications.event_handlers import _safe_dispatch
            from apps.system.repositories.system_repository import InstitutionRepository

            institution = InstitutionRepository().get_profile()
            institution_name = institution.institution_name if institution else "VoteBridge"

            for user, plain_pin, _row in payloads:
                _safe_dispatch(
                    "election_pin",
                    user,
                    {
                        "institution_name": institution_name,
                        "election_title": election.title,
                        "election_pin": plain_pin,
                    },
                    election=election,
                )
        except Exception:
            logger.exception("Failed to dispatch election PIN notifications for %s", election.uuid)


election_pin_service = ElectionPinService()
