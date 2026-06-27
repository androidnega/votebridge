import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.security.services.monitoring_service import resolve_ip_geolocation
from apps.trusted_devices.constants import DeviceType, TrustLevel
from apps.trusted_devices.models import TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceRepository
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.notification_service import trusted_device_notification_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service
from apps.trusted_devices.services.risk_score_service import device_risk_score_service
from apps.trusted_devices.services.session_revocation_service import trusted_device_session_revocation_service
from apps.trusted_devices.services.trust_level_service import device_trust_level_service
from apps.trusted_devices.utils import (
    DeviceContext,
    default_device_name,
    generate_device_token,
    hash_device_token,
)

logger = logging.getLogger("votebridge")


class TrustedDeviceRegistrationService:
    """Register or refresh a trusted device after successful biometric verification."""

    def __init__(self, repository: TrustedDeviceRepository | None = None):
        self.repository = repository or TrustedDeviceRepository()

    @transaction.atomic
    def register_after_biometric(
        self,
        user: User,
        context: DeviceContext,
        *,
        ip_address: str | None = None,
        device_type: str | None = None,
    ) -> tuple[str, object | None]:
        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_trusted_devices"):
            return "", None

        dtype = device_type or getattr(context, "device_type", None) or DeviceType.PERSONAL
        expiration_days = trusted_device_policy_service.expiration_days_for_device_type(dtype)
        expires_at = timezone.now() + timedelta(days=expiration_days)
        geo = resolve_ip_geolocation(ip_address or "")
        raw_token = generate_device_token()
        token_hash = hash_device_token(raw_token, str(user.uuid))
        device_name = context.device_name or default_device_name(context)
        composite_fp = context.fingerprint_signature()
        renewed = False

        existing = self.repository.find_by_fingerprint(user, composite_fp)
        if existing and not existing.is_revoked:
            renewed = True
            device = self.repository.update(
                existing,
                device_token_hash=token_hash,
                device_name=device_name,
                device_type=dtype,
                last_ip=ip_address,
                last_country=geo.get("country", ""),
                last_city=geo.get("city", ""),
                last_biometric=timezone.now(),
                last_verified=timezone.now(),
                expires_at=expires_at,
                is_trusted=True,
                is_revoked=False,
                trust_level=TrustLevel.HIGH,
                operating_system=context.operating_system,
                browser_name=context.browser_name,
                browser_version=context.browser_version,
                platform=context.platform,
                timezone=context.timezone,
                language=context.language,
                screen_resolution=context.screen_resolution,
            )
        else:
            self._enforce_device_limit(user, policy.get("max_trusted_devices_per_user", 5))
            device = self.repository.create(
                user=user,
                device_name=device_name,
                device_type=dtype,
                trust_level=TrustLevel.HIGH,
                device_token_hash=token_hash,
                browser_fingerprint=composite_fp,
                operating_system=context.operating_system,
                browser_name=context.browser_name,
                browser_version=context.browser_version,
                platform=context.platform,
                timezone=context.timezone,
                language=context.language,
                screen_resolution=context.screen_resolution,
                first_ip=ip_address,
                last_ip=ip_address,
                first_country=geo.get("country", ""),
                last_country=geo.get("country", ""),
                first_city=geo.get("city", ""),
                last_city=geo.get("city", ""),
                last_biometric=timezone.now(),
                last_verified=timezone.now(),
                expires_at=expires_at,
                is_trusted=True,
            )

        device_risk_score_service.record_biometric_success(device)
        device_trust_level_service.apply_trust_level(device)

        if policy.get("enable_device_audit"):
            event = (
                TrustedDeviceEvent.EventType.DEVICE_RENEWED
                if renewed
                else TrustedDeviceEvent.EventType.DEVICE_REGISTERED
            )
            trusted_device_audit_service.record(
                user=user,
                event_type=event,
                device=device,
                context=context,
                ip_address=ip_address,
                country=geo.get("country", ""),
                city=geo.get("city", ""),
                metadata={"device_type": dtype, "expires_at": expires_at.isoformat()},
            )

        if not renewed:
            trusted_device_notification_service.notify_device_registered(user, device)

        return raw_token, device

    def _enforce_device_limit(self, user: User, max_devices: int) -> None:
        active = list(self.repository.list_active_for_user(user).order_by("last_seen"))
        while len(active) >= max_devices:
            oldest = active.pop(0)
            self.repository.revoke(oldest)
            trusted_device_audit_service.record(
                user=user,
                event_type=TrustedDeviceEvent.EventType.DEVICE_REVOKED,
                device=oldest,
                metadata={"reason": "max_devices_exceeded"},
            )


trusted_device_registration_service = TrustedDeviceRegistrationService()
