import logging
import secrets

from django.core.cache import cache

from apps.accounts.models import User
from apps.accounts.repositories.auth_repository import SessionRepository
from apps.accounts.services.mfa_service import MFAService
from apps.biometrics.constants import HIGH_ASSURANCE_CACHE_PREFIX
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.notification_service import trusted_device_notification_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service

logger = logging.getLogger("votebridge")


class TrustedDeviceSessionRevocationService:
    """Live session termination when a trusted device is revoked."""

    def __init__(
        self,
        session_repository: SessionRepository | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.sessions = session_repository or SessionRepository()
        self.mfa_service = mfa_service or MFAService()

    def revoke_device_sessions(
        self,
        device: TrustedDevice,
        *,
        actor: User | None = None,
        ip_address: str | None = None,
    ) -> int:
        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_live_session_revocation", True):
            return 0

        count = self.sessions.revoke_all_for_user(device.user)
        self._invalidate_high_assurance(device.user)
        self._invalidate_device_token(device)

        trusted_device_audit_service.record(
            user=device.user,
            event_type=TrustedDeviceEvent.EventType.SESSION_REVOKED,
            device=device,
            ip_address=ip_address,
            metadata={
                "sessions_revoked": count,
                "revoked_by": str(actor.uuid) if actor else None,
            },
        )

        trusted_device_notification_service.notify_device_revoked(
            device.user,
            device,
            revoked_by=str(actor.uuid) if actor else "",
        )
        return count

    @staticmethod
    def _invalidate_high_assurance(user: User) -> None:
        latest_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:latest"
        token = cache.get(latest_key)
        if token:
            cache.delete(f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{token}")
            cache.delete(latest_key)

    @staticmethod
    def _invalidate_device_token(device: TrustedDevice) -> None:
        device.device_token_hash = secrets.token_hex(32)
        device.save(update_fields=["device_token_hash", "updated_at"])


trusted_device_session_revocation_service = TrustedDeviceSessionRevocationService()
