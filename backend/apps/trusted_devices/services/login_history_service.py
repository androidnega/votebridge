import logging

from django.utils import timezone

from apps.accounts.models import User
from apps.trusted_devices.constants import AUTH_METHOD_BIOMETRIC, AUTH_METHOD_TRUSTED
from apps.trusted_devices.models import TrustedDevice
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceLoginHistoryRepository
from apps.trusted_devices.utils import DeviceContext

logger = logging.getLogger("votebridge")


class TrustedDeviceLoginHistoryService:
    def __init__(self, repository: TrustedDeviceLoginHistoryRepository | None = None):
        self.repository = repository or TrustedDeviceLoginHistoryRepository()

    def record_login(
        self,
        *,
        user: User,
        device: TrustedDevice,
        context: DeviceContext,
        ip_address: str | None,
        country: str,
        city: str,
        authentication_method: str,
        risk_score: float,
    ) -> None:
        now = timezone.now()
        if device.last_seen:
            device.previous_login_at = device.last_seen
        device.last_seen = now
        device.save(update_fields=["previous_login_at", "last_seen", "updated_at"])

        self.repository.create(
            user=user,
            device=device,
            logged_in_at=now,
            country=country,
            city=city,
            browser_name=context.browser_name,
            operating_system=context.operating_system,
            authentication_method=authentication_method,
            risk_score=risk_score,
            ip_address=ip_address,
        )

    def get_history(self, device: TrustedDevice, *, limit: int = 10) -> list:
        return list(self.repository.list_for_device(device, limit=limit))

    def serialize_device_login_summary(self, device: TrustedDevice) -> dict:
        history = self.get_history(device, limit=2)
        last = history[0] if history else None
        previous = history[1] if len(history) > 1 else None
        return {
            "last_login": last.logged_in_at if last else device.last_seen,
            "previous_login": previous.logged_in_at if previous else device.previous_login_at,
            "last_country": last.country if last else device.last_country,
            "last_city": last.city if last else device.last_city,
            "last_browser": last.browser_name if last else device.browser_name,
            "last_os": last.operating_system if last else device.operating_system,
            "last_auth_method": last.authentication_method if last else "",
            "last_risk_score": last.risk_score if last else device.risk_score,
            "history": [
                {
                    "logged_in_at": h.logged_in_at,
                    "country": h.country,
                    "city": h.city,
                    "browser_name": h.browser_name,
                    "operating_system": h.operating_system,
                    "authentication_method": h.authentication_method,
                    "risk_score": h.risk_score,
                }
                for h in history
            ],
        }


trusted_device_login_history_service = TrustedDeviceLoginHistoryService()
