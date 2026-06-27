import logging
from datetime import timedelta

from django.utils import timezone

from apps.trusted_devices.constants import (
    BIOMETRIC_RECENT_HOURS,
    HIGH_TRUST_RISK_THRESHOLD,
    LOW_TRUST_RISK_THRESHOLD,
    TrustLevel,
)
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service

logger = logging.getLogger("votebridge")


class DeviceTrustLevelService:
    """Compute and persist device trust levels from verification and risk signals."""

    def compute_trust_level(self, device: TrustedDevice) -> str:
        if device.is_revoked or device.trust_level == TrustLevel.REVOKED:
            return TrustLevel.REVOKED

        if not device.is_trusted or device.expires_at <= timezone.now():
            return TrustLevel.LOW

        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_device_trust_levels", True):
            return TrustLevel.MEDIUM if device.is_valid else TrustLevel.LOW

        recent_biometric = False
        if device.last_biometric:
            recent_biometric = device.last_biometric >= timezone.now() - timedelta(hours=BIOMETRIC_RECENT_HOURS)

        if recent_biometric and device.risk_score < HIGH_TRUST_RISK_THRESHOLD:
            return TrustLevel.HIGH

        if device.risk_score >= LOW_TRUST_RISK_THRESHOLD:
            return TrustLevel.LOW

        return TrustLevel.MEDIUM

    def apply_trust_level(self, device: TrustedDevice, *, actor_metadata: dict | None = None) -> str:
        previous = device.trust_level
        new_level = self.compute_trust_level(device)
        if previous != new_level:
            device.trust_level = new_level
            device.save(update_fields=["trust_level", "updated_at"])
            if trusted_device_policy_service.get_policy().get("enable_device_audit", True):
                trusted_device_audit_service.record(
                    user=device.user,
                    event_type=TrustedDeviceEvent.EventType.TRUST_LEVEL_CHANGED,
                    device=device,
                    metadata={"previous": previous, "current": new_level, **(actor_metadata or {})},
                )
        return new_level


device_trust_level_service = DeviceTrustLevelService()
