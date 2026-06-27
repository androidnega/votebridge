import logging
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import MFALog, User
from apps.accounts.repositories.auth_repository import MFALogRepository
from apps.biometrics.services.audit_service import biometric_audit_service
from apps.biometrics.services.policy_service import biometric_policy_service
from apps.security.services.monitoring_service import resolve_ip_geolocation
from apps.trusted_devices.constants import (
    AUTH_METHOD_TRUSTED,
    BLOCK_RISK_THRESHOLD,
    COUNTRY_CHANGE_PENALTY,
    EXPIRED_TRUST_PENALTY,
    FAILED_LOGIN_PENALTY,
    FINGERPRINT_MISMATCH_PENALTY,
    HIGH_RISK_THRESHOLD,
    IMPOSSIBLE_TRAVEL_PENALTY,
    INVALID_TOKEN_PENALTY,
    MISSING_TOKEN_PENALTY,
    NEW_DEVICE_PENALTY,
    RISK_ALLOW,
    RISK_BLOCK,
    RISK_REQUIRE_BIOMETRIC,
    TrustLevel,
    UNKNOWN_BROWSER_PENALTY,
)
from apps.trusted_devices.models import TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceRepository
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.impossible_travel_service import impossible_travel_service
from apps.trusted_devices.services.notification_service import trusted_device_notification_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service
from apps.trusted_devices.services.risk_score_service import device_risk_score_service
from apps.trusted_devices.services.trust_level_service import device_trust_level_service
from apps.trusted_devices.utils import DeviceContext, fingerprint_match_score, hash_device_token

logger = logging.getLogger("votebridge")


@dataclass
class RiskDecision:
    action: str
    risk_score: float
    reasons: list[str]
    trusted_device: object | None = None
    trust_level: str | None = None


class RiskAssessmentService:
    """Multi-signal login risk evaluation — never IP address alone."""

    def __init__(
        self,
        device_repository: TrustedDeviceRepository | None = None,
        mfa_log_repository: MFALogRepository | None = None,
    ):
        self.devices = device_repository or TrustedDeviceRepository()
        self.mfa_logs = mfa_log_repository or MFALogRepository()

    def assess_login(
        self,
        user: User,
        *,
        ip_address: str | None,
        user_agent: str | None,
        context: DeviceContext,
        trusted_device_token: str | None = None,
        force_biometric: bool = False,
    ) -> RiskDecision:
        policy = trusted_device_policy_service.get_policy()
        bio_policy = biometric_policy_service.get_policy()
        reasons: list[str] = []
        score = 0.0
        trust_level = None

        if force_biometric:
            return RiskDecision(RISK_REQUIRE_BIOMETRIC, 100.0, ["manual_reverification"])

        if not biometric_policy_service.is_module_enabled():
            return RiskDecision(RISK_ALLOW, 0.0, ["biometrics_disabled"])

        if biometric_audit_service.is_student_user(user):
            return RiskDecision(RISK_ALLOW, 0.0, ["student_exempt"])

        if not biometric_audit_service.is_privileged_user(user):
            return RiskDecision(RISK_ALLOW, 0.0, ["not_privileged"])

        if not bio_policy.get("enable_face_verification"):
            return RiskDecision(RISK_ALLOW, 0.0, ["face_verification_disabled"])

        if not policy.get("enable_trusted_devices") or not policy.get("enable_risk_based_authentication"):
            return RiskDecision(RISK_REQUIRE_BIOMETRIC, 80.0, ["risk_based_disabled"])

        geo = resolve_ip_geolocation(ip_address or "")
        country = geo.get("country", "Unknown")
        city = geo.get("city", "")

        travel = impossible_travel_service.check(user, country=country, city=city)
        if travel.detected:
            score += IMPOSSIBLE_TRAVEL_PENALTY
            reasons.append("impossible_travel")
            trusted_device_notification_service.notify_impossible_travel(
                user, previous=travel.previous_location, current=travel.current_location
            )
            if travel.decision == RISK_BLOCK:
                return self._finalize(
                    user, RISK_BLOCK, score, reasons, None, None, context, ip_address, user_agent, country, city
                )
            return self._finalize(
                user,
                RISK_REQUIRE_BIOMETRIC,
                score,
                reasons,
                None,
                None,
                context,
                ip_address,
                user_agent,
                country,
                city,
            )

        failed_recent = self._recent_failed_logins(user)
        if failed_recent >= 5:
            score += BLOCK_RISK_THRESHOLD
            reasons.append("excessive_failed_logins")

        trusted_device = None
        if not trusted_device_token:
            score += MISSING_TOKEN_PENALTY
            reasons.append("missing_trusted_device_token")
        else:
            token_hash = hash_device_token(trusted_device_token.strip(), str(user.uuid))
            trusted_device = self.devices.get_by_token_hash(user, token_hash)
            if not trusted_device:
                score += INVALID_TOKEN_PENALTY
                reasons.append("invalid_trusted_device_token")
            elif trusted_device.trust_level == TrustLevel.REVOKED or trusted_device.is_revoked:
                score += BLOCK_RISK_THRESHOLD
                reasons.append("device_revoked")
            elif policy.get("enable_device_expiration", True) and trusted_device.expires_at <= timezone.now():
                score += EXPIRED_TRUST_PENALTY
                reasons.append("expired_trust")
                device_risk_score_service.apply_login_signals(trusted_device, expired_trust=True)
            elif not trusted_device.is_trusted:
                score += INVALID_TOKEN_PENALTY
                reasons.append("untrusted_device")
            else:
                trust_level = device_trust_level_service.compute_trust_level(trusted_device)
                if policy.get("enable_device_risk_scores", True):
                    score = max(score, trusted_device.risk_score * 0.5)

                match = fingerprint_match_score(trusted_device.browser_fingerprint, context)
                if policy.get("enable_device_fingerprinting") and match < 70.0:
                    score += FINGERPRINT_MISMATCH_PENALTY
                    reasons.append("fingerprint_mismatch")
                    if match < 40.0:
                        score += UNKNOWN_BROWSER_PENALTY
                        reasons.append("unknown_browser")

                country_changed = bool(
                    trusted_device.last_country
                    and country not in ("Unknown", "", trusted_device.last_country)
                )
                if country_changed:
                    if policy.get("require_biometrics_for_country_change"):
                        score += COUNTRY_CHANGE_PENALTY
                        reasons.append("country_change")
                    trusted_device_notification_service.notify_country_change(user, country=country, city=city)

                if trust_level == TrustLevel.LOW:
                    score += 20.0
                    reasons.append("low_trust_level")
                elif trust_level == TrustLevel.REVOKED:
                    score += BLOCK_RISK_THRESHOLD
                    reasons.append("revoked_trust_level")

        if not trusted_device:
            known = self.devices.find_by_fingerprint(user, context.fingerprint_signature())
            if not known and policy.get("require_biometrics_for_new_device"):
                score += NEW_DEVICE_PENALTY
                reasons.append("new_device")

        if failed_recent >= 3:
            score += FAILED_LOGIN_PENALTY
            reasons.append("recent_failed_attempts")

        max_risk = float(policy.get("maximum_risk_score", 100))
        score = min(score, max_risk)

        if score >= BLOCK_RISK_THRESHOLD or trust_level == TrustLevel.REVOKED:
            decision = RISK_BLOCK
        elif trust_level == TrustLevel.HIGH and score < 30.0 and trusted_device and trusted_device.is_valid:
            decision = RISK_ALLOW
        elif score >= HIGH_RISK_THRESHOLD or (
            policy.get("require_biometrics_for_high_risk") and score >= 50.0
        ):
            decision = RISK_REQUIRE_BIOMETRIC
            trusted_device_notification_service.notify_high_risk_login(
                user, risk_score=score, reasons=reasons
            )
        elif trusted_device and trusted_device.is_valid and trust_level in (TrustLevel.HIGH, TrustLevel.MEDIUM):
            if score < 30.0 and trust_level == TrustLevel.HIGH:
                decision = RISK_ALLOW
            elif score < 50.0 and trust_level == TrustLevel.MEDIUM:
                decision = RISK_ALLOW
            else:
                decision = RISK_REQUIRE_BIOMETRIC
        elif trusted_device and trusted_device.is_valid and score < 30.0:
            decision = RISK_ALLOW
        else:
            decision = RISK_REQUIRE_BIOMETRIC
            if "elevated_risk" not in reasons:
                reasons.append("elevated_risk")

        return self._finalize(
            user, decision, score, reasons, trusted_device, trust_level, context, ip_address, user_agent, country, city
        )

    def _finalize(
        self,
        user,
        decision,
        score,
        reasons,
        trusted_device,
        trust_level,
        context,
        ip_address,
        user_agent,
        country,
        city,
    ) -> RiskDecision:
        policy = trusted_device_policy_service.get_policy()
        if trusted_device and policy.get("enable_device_risk_scores"):
            device_risk_score_service.apply_login_signals(
                trusted_device,
                country_changed="country_change" in reasons,
                unknown_browser="unknown_browser" in reasons,
                expired_trust="expired_trust" in reasons,
                trusted_login=decision == RISK_ALLOW,
            )
            device_trust_level_service.apply_trust_level(trusted_device)
            trust_level = trusted_device.trust_level

        if policy.get("enable_device_audit"):
            event_type = TrustedDeviceEvent.EventType.TRUSTED_LOGIN
            if decision == RISK_REQUIRE_BIOMETRIC:
                event_type = TrustedDeviceEvent.EventType.BIOMETRIC_TRIGGERED
            if "country_change" in reasons:
                event_type = TrustedDeviceEvent.EventType.NEW_COUNTRY_LOGIN
            if score >= HIGH_RISK_THRESHOLD:
                event_type = TrustedDeviceEvent.EventType.HIGH_RISK_LOGIN
            if "impossible_travel" in reasons:
                event_type = TrustedDeviceEvent.EventType.IMPOSSIBLE_TRAVEL

            trusted_device_audit_service.record(
                user=user,
                event_type=event_type,
                device=trusted_device,
                decision=decision,
                risk_score=score,
                context=context,
                ip_address=ip_address,
                user_agent=user_agent,
                country=country,
                city=city,
                metadata={"reasons": reasons, "trust_level": trust_level},
            )

        return RiskDecision(decision, score, reasons, trusted_device, trust_level)

    def _recent_failed_logins(self, user: User) -> int:
        since = timezone.now() - timedelta(hours=24)
        return self.mfa_logs.get_queryset().filter(
            user=user,
            event_type=MFALog.EventType.LOGIN_FAILED,
            created_at__gte=since,
        ).count()


risk_assessment_service = RiskAssessmentService()
