from django.conf import settings

from apps.accounts.models import Role, User
from apps.biometrics.constants import (
    DEFAULT_LIVENESS_THRESHOLD,
    DEFAULT_LOCKOUT_MINUTES,
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_SESSION_TIMEOUT_MINUTES,
)
from apps.system.repositories.system_repository import FeatureFlagRepository, SystemSettingRepository

BIOMETRIC_AUTH_DISABLED_MESSAGE = (
    "Biometric authentication is currently disabled for this deployment "
    "and can be enabled in a future release."
)


class BiometricPolicyService:
    """Reads Identity Assurance settings from System Control Center."""

    CATEGORY = "identity_assurance"

    def __init__(
        self,
        settings_repository: SystemSettingRepository | None = None,
        feature_flag_repository: FeatureFlagRepository | None = None,
    ):
        self.settings = settings_repository or SystemSettingRepository()
        self.feature_flags = feature_flag_repository or FeatureFlagRepository()

    def _get_value(self, key: str, default):
        setting = self.settings.get_by_key(f"{self.CATEGORY}.{key}")
        if not setting:
            return default
        return setting.value.get("value", default)

    def is_auth_enabled(self) -> bool:
        """Deployment gate — when False, login never requires biometrics (v1.0 default)."""
        return bool(getattr(settings, "BIOMETRIC_AUTH_ENABLED", False))

    def is_module_enabled(self) -> bool:
        if not self.is_auth_enabled():
            return False
        flag = self.feature_flags.get_by_key("future_biometrics")
        return bool(flag.enabled) if flag else False

    def get_policy(self) -> dict:
        auth_enabled = self.is_auth_enabled()
        module_enabled = self.is_module_enabled()
        return {
            "auth_enabled": auth_enabled,
            "enabled": module_enabled,
            "deployment_status": "disabled" if not auth_enabled else ("active" if module_enabled else "configured_off"),
            "deployment_message": BIOMETRIC_AUTH_DISABLED_MESSAGE if not auth_enabled else "",
            "enable_face_verification": self._get_value("enable_face_verification", True),
            "enable_passive_liveness": self._get_value("enable_passive_liveness", True),
            "enable_active_liveness": self._get_value("enable_active_liveness", True),
            "enable_blink_challenge": self._get_value("enable_blink_challenge", True),
            "enable_left_turn": self._get_value("enable_left_turn", True),
            "enable_right_turn": self._get_value("enable_right_turn", True),
            "random_challenge": self._get_value("random_challenge", True),
            "matching_threshold": float(self._get_value("matching_threshold", DEFAULT_MATCH_THRESHOLD)),
            "liveness_threshold": float(self._get_value("liveness_threshold", DEFAULT_LIVENESS_THRESHOLD)),
            "maximum_attempts": int(self._get_value("maximum_attempts", DEFAULT_MAX_ATTEMPTS)),
            "session_timeout_minutes": int(self._get_value("session_timeout_minutes", DEFAULT_SESSION_TIMEOUT_MINUTES)),
            "enable_verification_snapshots": self._get_value("enable_verification_snapshots", False),
            "enable_confidence_logging": self._get_value("enable_confidence_logging", True),
            "enable_audit": self._get_value("enable_audit", True),
            "lockout_minutes": int(self._get_value("lockout_minutes", DEFAULT_LOCKOUT_MINUTES)),
        }

    def requires_verification_at_login(self, user: User) -> bool:
        from apps.biometrics.services.audit_service import biometric_audit_service

        if not self.is_module_enabled():
            return False
        if biometric_audit_service.is_student_user(user):
            return False
        if not biometric_audit_service.is_privileged_user(user):
            return False
        policy = self.get_policy()
        return policy.get("enable_face_verification", True)

    def requires_step_up(self, user: User, action: str) -> bool:
        from apps.biometrics.constants import STEP_UP_ACTIONS
        from apps.biometrics.services.audit_service import biometric_audit_service

        if not self.is_module_enabled():
            return False
        if not biometric_audit_service.is_privileged_user(user):
            return False
        if action not in STEP_UP_ACTIONS:
            return False
        return self.get_policy().get("enable_face_verification", True)

    def can_enroll_target(self, actor: User, target: User) -> bool:
        if actor.role.name != Role.Name.SUPER_ADMIN:
            return False
        if target.role.name not in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return False
        return True


biometric_policy_service = BiometricPolicyService()
