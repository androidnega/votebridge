import logging
from dataclasses import dataclass

from apps.accounts.models import MFALog, User
from apps.accounts.services.mfa_service import MFAService
from apps.security.models import AuditLog
from apps.security.services.monitoring_service import monitoring_service
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceEventRepository
from apps.trusted_devices.utils import DeviceContext

logger = logging.getLogger("votebridge")

MFA_EVENT_MAP = {
    TrustedDeviceEvent.EventType.DEVICE_REGISTERED: MFALog.EventType.DEVICE_REGISTERED,
    TrustedDeviceEvent.EventType.DEVICE_REVOKED: MFALog.EventType.DEVICE_REVOKED,
    TrustedDeviceEvent.EventType.DEVICE_EXPIRED: MFALog.EventType.DEVICE_EXPIRED,
    TrustedDeviceEvent.EventType.TRUSTED_LOGIN: MFALog.EventType.TRUSTED_LOGIN,
    TrustedDeviceEvent.EventType.HIGH_RISK_LOGIN: MFALog.EventType.HIGH_RISK_LOGIN,
    TrustedDeviceEvent.EventType.NEW_COUNTRY_LOGIN: MFALog.EventType.NEW_COUNTRY_LOGIN,
    TrustedDeviceEvent.EventType.BIOMETRIC_TRIGGERED: MFALog.EventType.BIOMETRIC_TRIGGERED,
    TrustedDeviceEvent.EventType.DEVICE_RENAMED: MFALog.EventType.DEVICE_RENAMED,
    TrustedDeviceEvent.EventType.TRUST_LEVEL_CHANGED: MFALog.EventType.TRUST_LEVEL_CHANGED,
    TrustedDeviceEvent.EventType.RISK_SCORE_CHANGED: MFALog.EventType.RISK_SCORE_CHANGED,
    TrustedDeviceEvent.EventType.IMPOSSIBLE_TRAVEL: MFALog.EventType.IMPOSSIBLE_TRAVEL,
    TrustedDeviceEvent.EventType.DEVICE_RENEWED: MFALog.EventType.DEVICE_RENEWED,
    TrustedDeviceEvent.EventType.SESSION_REVOKED: MFALog.EventType.SESSION_REVOKED,
    TrustedDeviceEvent.EventType.UNIVERSITY_DEVICE_ASSIGNED: MFALog.EventType.UNIVERSITY_DEVICE_ASSIGNED,
}


class TrustedDeviceAuditService:
    def __init__(
        self,
        repository: TrustedDeviceEventRepository | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.repository = repository or TrustedDeviceEventRepository()
        self.mfa_service = mfa_service or MFAService()

    def record(
        self,
        *,
        user: User | None,
        event_type: str,
        device: TrustedDevice | None = None,
        decision: str = "",
        risk_score: float | None = None,
        context: DeviceContext | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        country: str = "",
        city: str = "",
        metadata: dict | None = None,
    ) -> TrustedDeviceEvent:
        ctx = context or DeviceContext(browser_fingerprint="")
        event = self.repository.create(
            user=user,
            device=device,
            event_type=event_type,
            decision=decision,
            risk_score=risk_score,
            browser_name=ctx.browser_name,
            operating_system=ctx.operating_system,
            country=country,
            city=city,
            ip_address=ip_address,
            user_agent=user_agent or "",
            metadata=metadata or {},
        )

        mfa_type = MFA_EVENT_MAP.get(event_type)
        if mfa_type:
            self.mfa_service.log(
                event_type=mfa_type,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={
                    "subsystem": "trusted_devices",
                    "event_type": event_type,
                    "decision": decision,
                    "risk_score": risk_score,
                    "device_uuid": str(device.uuid) if device else None,
                    **(metadata or {}),
                },
            )

        monitoring_service.record_event(
            event_type=AuditLog.EventType.ADMIN_ACTION,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            browser_fingerprint=ctx.browser_fingerprint,
            metadata={
                "subsystem": "trusted_devices",
                "trusted_device_event": event_type,
                "decision": decision,
                "risk_score": risk_score,
                **(metadata or {}),
            },
        )
        return event


trusted_device_audit_service = TrustedDeviceAuditService()
