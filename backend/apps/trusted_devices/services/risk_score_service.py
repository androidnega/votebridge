import logging

from apps.trusted_devices.constants import MAX_DEVICE_RISK_SCORE
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service
from apps.trusted_devices.services.trust_level_service import device_trust_level_service

logger = logging.getLogger("votebridge")

# Risk score deltas
DELTA_COUNTRY_CHANGE = 20.0
DELTA_FAILED_LOGIN = 10.0
DELTA_UNKNOWN_BROWSER = 12.0
DELTA_EXPIRED_TRUST = 25.0
DELTA_BIOMETRIC_FAILURE = 15.0
DELTA_SPOOF_ATTEMPT = 30.0
DELTA_SUCCESSFUL_BIOMETRIC = -25.0
DELTA_TRUSTED_LOGIN = -5.0
DELTA_UNIVERSITY_DEVICE = -10.0


class DeviceRiskScoreService:
    """Maintain per-device risk score (0–100) used by RiskAssessmentService."""

    def _clamp(self, score: float) -> float:
        return max(0.0, min(MAX_DEVICE_RISK_SCORE, score))

    def set_score(self, device: TrustedDevice, score: float, *, reason: str = "") -> float:
        if not trusted_device_policy_service.get_policy().get("enable_device_risk_scores", True):
            return device.risk_score

        previous = device.risk_score
        device.risk_score = self._clamp(score)
        device.save(update_fields=["risk_score", "updated_at"])

        if previous != device.risk_score and trusted_device_policy_service.get_policy().get("enable_device_audit"):
            trusted_device_audit_service.record(
                user=device.user,
                event_type=TrustedDeviceEvent.EventType.RISK_SCORE_CHANGED,
                device=device,
                risk_score=device.risk_score,
                metadata={"previous": previous, "reason": reason},
            )
        device_trust_level_service.apply_trust_level(device)
        return device.risk_score

    def adjust(self, device: TrustedDevice, delta: float, *, reason: str = "") -> float:
        return self.set_score(device, device.risk_score + delta, reason=reason)

    def apply_login_signals(
        self,
        device: TrustedDevice | None,
        *,
        country_changed: bool = False,
        unknown_browser: bool = False,
        expired_trust: bool = False,
        trusted_login: bool = False,
    ) -> float | None:
        if not device:
            return None
        delta = 0.0
        if country_changed:
            delta += DELTA_COUNTRY_CHANGE
        if unknown_browser:
            delta += DELTA_UNKNOWN_BROWSER
        if expired_trust:
            delta += DELTA_EXPIRED_TRUST
        if trusted_login:
            delta += DELTA_TRUSTED_LOGIN
        if device.device_type == "university_managed":
            delta += DELTA_UNIVERSITY_DEVICE
        if delta == 0:
            return device.risk_score
        return self.adjust(device, delta, reason="login_signals")

    def record_biometric_success(self, device: TrustedDevice) -> float:
        return self.adjust(device, DELTA_SUCCESSFUL_BIOMETRIC, reason="biometric_success")

    def record_biometric_failure(self, device: TrustedDevice) -> float:
        return self.adjust(device, DELTA_BIOMETRIC_FAILURE, reason="biometric_failure")

    def record_spoof_attempt(self, device: TrustedDevice) -> float:
        return self.adjust(device, DELTA_SPOOF_ATTEMPT, reason="spoof_attempt")


device_risk_score_service = DeviceRiskScoreService()
