import logging

from apps.accounts.models import MFALog, Role, User
from apps.accounts.services.mfa_service import MFAService
from apps.biometrics.constants import PRIVILEGED_ROLES, PRIVILEGED_USERNAMES
from apps.biometrics.models import BiometricVerificationLog
from apps.biometrics.repositories.biometric_repository import BiometricVerificationLogRepository
from apps.security.models import AuditLog
from apps.security.services.monitoring_service import monitoring_service

logger = logging.getLogger("votebridge")

MFA_EVENT_MAP = {
    BiometricVerificationLog.EventType.ENROLLMENT: MFALog.EventType.BIO_ENROLLMENT,
    BiometricVerificationLog.EventType.VERIFICATION_PASSED: MFALog.EventType.BIO_VERIFY_PASS,
    BiometricVerificationLog.EventType.VERIFICATION_FAILED: MFALog.EventType.BIO_VERIFY_FAIL,
    BiometricVerificationLog.EventType.CHALLENGE_FAILED: MFALog.EventType.BIO_CHALLENGE_FAIL,
    BiometricVerificationLog.EventType.SPOOF_ATTEMPT: MFALog.EventType.BIO_SPOOF_ATTEMPT,
    BiometricVerificationLog.EventType.ACCOUNT_LOCKED: MFALog.EventType.BIO_ACCOUNT_LOCKED,
    BiometricVerificationLog.EventType.STRONGROOM_VERIFICATION: MFALog.EventType.BIO_STRONGROOM,
    BiometricVerificationLog.EventType.STEP_UP: MFALog.EventType.BIO_STEP_UP,
}


class BiometricAuditService:
    """Dual audit trail — local log + MFALog + central AuditLog."""

    def __init__(
        self,
        log_repository: BiometricVerificationLogRepository | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.repository = log_repository or BiometricVerificationLogRepository()
        self.mfa_service = mfa_service or MFAService()

    def record(
        self,
        *,
        user: User | None,
        event_type: str,
        outcome: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        challenge_type: str = "",
        confidence: float | None = None,
        liveness_score: float | None = None,
        processing_time_ms: int | None = None,
        model_version: str = "",
        device_fingerprint: str = "",
        metadata: dict | None = None,
    ) -> BiometricVerificationLog:
        safe_metadata = {k: v for k, v in (metadata or {}).items() if "embedding" not in k.lower()}

        log_entry = self.repository.create(
            user=user,
            event_type=event_type,
            outcome=outcome,
            challenge_type=challenge_type,
            confidence=confidence,
            liveness_score=liveness_score,
            processing_time_ms=processing_time_ms,
            model_version=model_version,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent or "",
            metadata=safe_metadata,
        )

        mfa_event = MFA_EVENT_MAP.get(event_type, MFALog.EventType.BIO_VERIFY_FAIL)
        self.mfa_service.log(
            event_type=mfa_event,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "subsystem": "biometrics",
                "event_type": event_type,
                "outcome": outcome,
                "challenge_type": challenge_type,
                "confidence": confidence,
                "liveness_score": liveness_score,
                "model_version": model_version,
                **safe_metadata,
            },
        )

        monitoring_service.record_event(
            event_type=AuditLog.EventType.ADMIN_ACTION,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "subsystem": "biometrics",
                "biometric_event": event_type,
                "outcome": outcome,
                "challenge_type": challenge_type,
                "confidence": confidence,
                "liveness_score": liveness_score,
                "model_version": model_version,
                **safe_metadata,
            },
        )
        return log_entry

    @staticmethod
    def is_privileged_user(user: User) -> bool:
        if not user or not user.is_active:
            return False
        role_name = user.role.name if user.role_id else ""
        if role_name in PRIVILEGED_ROLES:
            return True
        return user.username in PRIVILEGED_USERNAMES

    @staticmethod
    def is_student_user(user: User) -> bool:
        role_name = user.role.name if user.role_id else ""
        return role_name in {Role.Name.STUDENT, Role.Name.CANDIDATE}


biometric_audit_service = BiometricAuditService()
