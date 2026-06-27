from apps.system.repositories.system_repository import SystemSettingRepository


class TrustedDevicePolicyService:
    """Reads trusted device settings from Identity Assurance SCC category."""

    CATEGORY = "identity_assurance"

    def __init__(self, settings_repository: SystemSettingRepository | None = None):
        self.settings = settings_repository or SystemSettingRepository()

    def _get_value(self, key: str, default):
        setting = self.settings.get_by_key(f"{self.CATEGORY}.{key}")
        if not setting:
            return default
        return setting.value.get("value", default)

    def get_policy(self) -> dict:
        from apps.trusted_devices.constants import (
            DEFAULT_MAX_TRUSTED_DEVICES,
            DEFAULT_PERSONAL_DEVICE_EXPIRATION_DAYS,
            DEFAULT_TRUSTED_DEVICE_EXPIRATION_DAYS,
            DEFAULT_UNIVERSITY_DEVICE_EXPIRATION_DAYS,
            MAX_DEVICE_RISK_SCORE,
        )

        return {
            "enable_trusted_devices": self._get_value("enable_trusted_devices", True),
            "enable_risk_based_authentication": self._get_value("enable_risk_based_authentication", True),
            "trusted_device_expiration_days": int(
                self._get_value("trusted_device_expiration_days", DEFAULT_TRUSTED_DEVICE_EXPIRATION_DAYS)
            ),
            "university_device_expiration_days": int(
                self._get_value("university_device_expiration_days", DEFAULT_UNIVERSITY_DEVICE_EXPIRATION_DAYS)
            ),
            "personal_device_expiration_days": int(
                self._get_value("personal_device_expiration_days", DEFAULT_PERSONAL_DEVICE_EXPIRATION_DAYS)
            ),
            "max_trusted_devices_per_user": int(
                self._get_value("max_trusted_devices_per_user", DEFAULT_MAX_TRUSTED_DEVICES)
            ),
            "require_biometrics_for_new_device": self._get_value("require_biometrics_for_new_device", True),
            "require_biometrics_for_country_change": self._get_value("require_biometrics_for_country_change", True),
            "require_biometrics_for_high_risk": self._get_value("require_biometrics_for_high_risk", True),
            "enable_device_fingerprinting": self._get_value("enable_device_fingerprinting", True),
            "enable_trusted_device_cookie_rotation": self._get_value(
                "enable_trusted_device_cookie_rotation", True
            ),
            "enable_device_audit": self._get_value("enable_device_audit", True),
            "enable_administrator_device_management": self._get_value(
                "enable_administrator_device_management", True
            ),
            "invalidate_trusted_device_on_logout": self._get_value("invalidate_trusted_device_on_logout", False),
            # Phase 21.6
            "enable_device_trust_levels": self._get_value("enable_device_trust_levels", True),
            "enable_impossible_travel_detection": self._get_value("enable_impossible_travel_detection", True),
            "enable_device_expiration": self._get_value("enable_device_expiration", True),
            "enable_device_notifications": self._get_value("enable_device_notifications", True),
            "enable_device_risk_scores": self._get_value("enable_device_risk_scores", True),
            "enable_high_assurance_indicator": self._get_value("enable_high_assurance_indicator", True),
            "enable_live_session_revocation": self._get_value("enable_live_session_revocation", True),
            "enable_university_device_policies": self._get_value("enable_university_device_policies", True),
            "maximum_trust_duration_days": int(
                self._get_value("maximum_trust_duration_days", DEFAULT_UNIVERSITY_DEVICE_EXPIRATION_DAYS)
            ),
            "maximum_risk_score": float(self._get_value("maximum_risk_score", MAX_DEVICE_RISK_SCORE)),
            "impossible_travel_threshold_minutes": int(
                self._get_value("impossible_travel_threshold_minutes", 120)
            ),
            "impossible_travel_action": self._get_value("impossible_travel_action", "REQUIRE_BIOMETRIC"),
        }

    def is_enabled(self) -> bool:
        return bool(self.get_policy().get("enable_trusted_devices", True))

    def expiration_days_for_device_type(self, device_type: str) -> int:
        policy = self.get_policy()
        if not policy.get("enable_university_device_policies", True):
            return policy.get("trusted_device_expiration_days", 90)
        if device_type == "university_managed":
            return min(
                policy.get("university_device_expiration_days", 180),
                policy.get("maximum_trust_duration_days", 180),
            )
        return policy.get("personal_device_expiration_days", 60)


trusted_device_policy_service = TrustedDevicePolicyService()
