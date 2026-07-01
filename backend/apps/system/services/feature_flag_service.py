"""
Centralized platform feature availability — single source of truth.

All modules must consult FeatureFlagService before enabling channel behaviour.
Toggle features only via System Control → Feature Flags.
"""

from django.core.cache import cache

from apps.system.models import FeatureFlag
from apps.system.repositories.system_repository import FeatureFlagRepository
from apps.system.utils import invalidate_settings_cache
from core.exceptions import NotFoundError, ValidationError

DEFAULT_FEATURE_FLAGS = [
    ("ussd", "USSD Voting", "Enable USSD voting channel"),
    ("sms", "SMS Notifications", "Enable SMS delivery and OTP via SMS"),
    ("email_notifications", "Email Notifications", "Enable email delivery and OTP via email"),
    ("otp_authentication", "OTP Authentication", "Require OTP verification for sign-in"),
    ("trusted_devices", "Trusted Devices", "Enable trusted device recognition at login"),
    ("maintenance_mode", "Maintenance Mode", "Allow platform maintenance mode controls"),
    ("fraud_detection", "Fraud Detection", "Enable fraud detection and alerting"),
    ("strongroom", "Strongroom", "Enable strongroom ballot integrity module"),
    ("realtime", "Realtime", "Enable WebSocket realtime updates"),
    ("analytics", "Analytics", "Enable analytics dashboards"),
    ("notifications", "Notifications", "Enable notification centre and campaign delivery"),
    ("monitoring", "Monitoring", "Enable operations monitoring"),
    ("future_ai", "Future AI", "Reserved for AI-assisted fraud analysis"),
    ("future_face_verification", "Future Face Verification", "Reserved for face verification"),
    ("future_biometrics", "Future Biometrics", "Reserved for biometric verification"),
]

# Legacy system settings mirrored by feature flags — not editable on integration pages.
FLAG_MANAGED_SETTING_KEYS = {
    "ussd.voting_enabled": "ussd",
    "notifications.election_notifications_enabled": "notifications",
    "notifications.result_notifications_enabled": "notifications",
    "identity_assurance.enable_trusted_devices": "trusted_devices",
}

CHANNEL_FLAG_KEYS = {
    "sms": "sms",
    "email": "email_notifications",
    "in_app": "notifications",
}


class FeatureFlagService:
    """Single source of truth for platform feature toggles."""

    USSD = "ussd"
    SMS = "sms"
    EMAIL = "email_notifications"
    OTP = "otp_authentication"
    TRUSTED_DEVICES = "trusted_devices"
    MAINTENANCE = "maintenance_mode"
    NOTIFICATIONS = "notifications"

    CACHE_PREFIX = "feature_flag:"
    CACHE_TTL_SECONDS = 60

    def __init__(self, repository: FeatureFlagRepository | None = None):
        self.repository = repository or FeatureFlagRepository()

    def _audit(self):
        from apps.system.services.system_service import SystemAuditService

        return SystemAuditService()

    def ensure_defaults(self):
        for key, name, description in DEFAULT_FEATURE_FLAGS:
            if self.repository.get_by_key(key):
                continue
            FeatureFlag.objects.create(key=key, name=name, description=description, enabled=True)
            self._invalidate_cache(key)

    def list_flags(self) -> list[dict]:
        return [self._serialize(flag) for flag in self.repository.list_all()]

    def is_enabled(self, key: str) -> bool:
        cache_key = f"{self.CACHE_PREFIX}{key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return bool(cached)

        flag = self.repository.get_by_key(key)
        enabled = flag.enabled if flag else True
        cache.set(cache_key, enabled, self.CACHE_TTL_SECONDS)
        return enabled

    def is_setting_managed_by_flag(self, full_key: str) -> bool:
        return full_key in FLAG_MANAGED_SETTING_KEYS

    def flag_for_setting(self, full_key: str) -> str | None:
        return FLAG_MANAGED_SETTING_KEYS.get(full_key)

    def is_channel_enabled(self, channel: str) -> bool:
        flag_key = CHANNEL_FLAG_KEYS.get(channel)
        if not flag_key:
            return True
        return self.is_enabled(flag_key)

    def is_ussd_enabled(self) -> bool:
        return self.is_enabled(self.USSD)

    def is_sms_enabled(self) -> bool:
        return self.is_enabled(self.SMS)

    def is_email_enabled(self) -> bool:
        return self.is_enabled(self.EMAIL)

    def is_otp_enabled(self) -> bool:
        return self.is_enabled(self.OTP)

    def is_trusted_devices_enabled(self) -> bool:
        return self.is_enabled(self.TRUSTED_DEVICES)

    def require_enabled(self, key: str, *, message: str | None = None) -> None:
        if not self.is_enabled(key):
            raise ValidationError(
                message=message or f"Feature '{key}' is disabled.",
                code="feature_disabled",
            )

    def update_flag(self, user, key: str, enabled: bool, *, step_up_token: str, request=None) -> dict:
        from apps.system.services.step_up_service import step_up_auth_service

        step_up_auth_service.validate_token(user, step_up_token)
        flag = self.repository.get_by_key(key)
        if not flag:
            raise NotFoundError(message=f"Feature flag not found: {key}", code="flag_not_found")
        flag.enabled = enabled
        flag.last_changed_by = user
        self.repository.save(flag)
        self._invalidate_cache(key)
        invalidate_settings_cache()
        if key == self.MAINTENANCE:
            self._sync_maintenance_mode(enabled)
        self._audit().record(user, "feature_flag_toggled", metadata={"key": key, "enabled": enabled}, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(flag)

    def _invalidate_cache(self, key: str) -> None:
        cache.delete(f"{self.CACHE_PREFIX}{key}")

    def _sync_maintenance_mode(self, enabled: bool) -> None:
        from apps.system.repositories.system_repository import MaintenanceRepository

        state = MaintenanceRepository().get_or_create_state()
        if state.is_enabled != enabled:
            state.is_enabled = enabled
            state.save(update_fields=["is_enabled", "updated_at"])
        cache.delete("system:maintenance")

    def _serialize(self, flag: FeatureFlag) -> dict:
        return {
            "uuid": str(flag.uuid),
            "key": flag.key,
            "name": flag.name,
            "description": flag.description,
            "enabled": flag.enabled,
            "last_changed_by": flag.last_changed_by.email if flag.last_changed_by else None,
            "last_changed_at": flag.last_changed_at.isoformat(),
        }


feature_flag_service = FeatureFlagService()
