import logging
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import User
from apps.trusted_devices.constants import IMPOSSIBLE_TRAVEL_PENALTY, RISK_BLOCK, RISK_REQUIRE_BIOMETRIC
from apps.trusted_devices.models import TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceLoginHistoryRepository
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service

logger = logging.getLogger("votebridge")


@dataclass
class ImpossibleTravelResult:
    detected: bool
    decision: str
    minutes_elapsed: float
    previous_location: str
    current_location: str
    reason: str = ""


class ImpossibleTravelService:
    """Detect geographically implausible login velocity (never IP address alone)."""

    def __init__(self, history_repository: TrustedDeviceLoginHistoryRepository | None = None):
        self.history = history_repository or TrustedDeviceLoginHistoryRepository()

    def check(
        self,
        user: User,
        *,
        country: str,
        city: str,
        login_time=None,
    ) -> ImpossibleTravelResult:
        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_impossible_travel_detection", True):
            return ImpossibleTravelResult(False, "", 0, "", "", "disabled")

        login_time = login_time or timezone.now()
        last = self.history.get_last_for_user(user)
        if not last:
            return ImpossibleTravelResult(False, "", 0, "", self._location(country, city))

        prev_location = self._location(last.country, last.city)
        curr_location = self._location(country, city)
        if not last.country or not country or last.country in ("Unknown", "Local", "Private"):
            return ImpossibleTravelResult(False, "", 0, prev_location, curr_location, "insufficient_geo")

        if last.country == country and (not last.city or not city or last.city == city):
            return ImpossibleTravelResult(False, "", 0, prev_location, curr_location)

        minutes = (login_time - last.logged_in_at).total_seconds() / 60.0
        threshold = float(policy.get("impossible_travel_threshold_minutes", 120))

        if minutes > threshold:
            return ImpossibleTravelResult(False, minutes, prev_location, curr_location, "within_travel_window")

        block_on_impossible = policy.get("impossible_travel_action", "REQUIRE_BIOMETRIC") == "BLOCK"
        decision = RISK_BLOCK if block_on_impossible else RISK_REQUIRE_BIOMETRIC

        trusted_device_audit_service.record(
            user=user,
            event_type=TrustedDeviceEvent.EventType.IMPOSSIBLE_TRAVEL,
            decision=decision,
            risk_score=IMPOSSIBLE_TRAVEL_PENALTY,
            country=country,
            city=city,
            metadata={
                "previous_location": prev_location,
                "current_location": curr_location,
                "minutes_elapsed": minutes,
            },
        )

        return ImpossibleTravelResult(
            detected=True,
            decision=decision,
            minutes_elapsed=minutes,
            previous_location=prev_location,
            current_location=curr_location,
            reason="impossible_travel",
        )

    @staticmethod
    def _location(country: str, city: str) -> str:
        if city and country:
            return f"{city}, {country}"
        return country or city or "Unknown"


impossible_travel_service = ImpossibleTravelService()
