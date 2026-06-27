import logging

from django.utils import timezone

from apps.trusted_devices.models import TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceRepository
from apps.trusted_devices.services.audit_service import trusted_device_audit_service

logger = logging.getLogger("votebridge")


class TrustedDeviceCleanupService:
    def __init__(self, repository: TrustedDeviceRepository | None = None):
        self.repository = repository or TrustedDeviceRepository()

    def expire_stale_devices(self) -> int:
        expired = self.repository.list_expired()
        count = 0
        for device in expired:
            self.repository.revoke(device)
            trusted_device_audit_service.record(
                user=device.user,
                event_type=TrustedDeviceEvent.EventType.DEVICE_EXPIRED,
                device=device,
                metadata={"expired_at": timezone.now().isoformat()},
            )
            count += 1
        return count


trusted_device_cleanup_service = TrustedDeviceCleanupService()
