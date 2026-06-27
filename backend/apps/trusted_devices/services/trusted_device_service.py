import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.security.services.monitoring_service import resolve_ip_geolocation
from apps.trusted_devices.constants import AUTH_METHOD_TRUSTED, TrustLevel
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent
from apps.trusted_devices.repositories.trusted_device_repository import TrustedDeviceRepository
from apps.trusted_devices.services.audit_service import trusted_device_audit_service
from apps.trusted_devices.services.login_history_service import trusted_device_login_history_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service
from apps.trusted_devices.services.session_revocation_service import trusted_device_session_revocation_service
from apps.trusted_devices.utils import (
    DeviceContext,
    fingerprint_match_score,
    hash_device_token,
)
from core.exceptions import NotFoundError, PermissionDeniedError

logger = logging.getLogger("votebridge")


class TrustedDeviceService:
    def __init__(self, repository: TrustedDeviceRepository | None = None):
        self.repository = repository or TrustedDeviceRepository()

    def list_devices(self, user: User) -> list[TrustedDevice]:
        return list(self.repository.list_for_user(user))

    def get_device(self, user: User, device_uuid) -> TrustedDevice:
        device = self.repository.get_by_uuid(device_uuid)
        if not device or device.user_id != user.id:
            raise NotFoundError(message="Trusted device not found.", code="device_not_found")
        return device

    def validate_token(
        self,
        user: User,
        raw_token: str | None,
        context: DeviceContext,
    ) -> TrustedDevice | None:
        if not raw_token or not raw_token.strip():
            return None

        token_hash = hash_device_token(raw_token.strip(), str(user.uuid))
        device = self.repository.get_by_token_hash(user, token_hash)
        if not device or not device.is_valid:
            return None

        match = fingerprint_match_score(device.browser_fingerprint, context)
        if match < 50.0:
            return None

        return device

    def touch_device(
        self,
        device: TrustedDevice,
        *,
        ip_address: str | None,
        context: DeviceContext,
        risk_score: float = 0.0,
    ) -> TrustedDevice:
        geo = resolve_ip_geolocation(ip_address or "")
        device.last_ip = ip_address
        device.last_country = geo.get("country", "")
        device.last_city = geo.get("city", "")
        device.last_seen = timezone.now()
        device.last_verified = timezone.now()
        device.risk_score = risk_score
        device.save(
            update_fields=[
                "last_ip",
                "last_country",
                "last_city",
                "last_seen",
                "last_verified",
                "risk_score",
                "updated_at",
            ]
        )
        from apps.trusted_devices.services.trust_level_service import device_trust_level_service

        device_trust_level_service.apply_trust_level(device)
        trusted_device_login_history_service.record_login(
            user=device.user,
            device=device,
            context=context,
            ip_address=ip_address,
            country=geo.get("country", ""),
            city=geo.get("city", ""),
            authentication_method=AUTH_METHOD_TRUSTED,
            risk_score=risk_score,
        )
        return device

    def rename_device(self, actor: User, device_uuid, name: str) -> TrustedDevice:
        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_administrator_device_management"):
            raise PermissionDeniedError(message="Device management is disabled.", code="management_disabled")

        device = self.get_device(actor, device_uuid)
        device.device_name = (name or "").strip()[:128] or device.device_name
        device.save(update_fields=["device_name", "updated_at"])

        from apps.trusted_devices.models import TrustedDeviceEvent

        trusted_device_audit_service.record(
            user=actor,
            event_type=TrustedDeviceEvent.EventType.DEVICE_RENAMED,
            device=device,
            metadata={"device_name": device.device_name},
        )
        return device

    def revoke_device(self, actor: User, device_uuid, *, target_user: User | None = None) -> TrustedDevice:
        policy = trusted_device_policy_service.get_policy()
        if not policy.get("enable_administrator_device_management"):
            raise PermissionDeniedError(message="Device management is disabled.", code="management_disabled")

        device = self.repository.get_by_uuid(device_uuid)
        if not device:
            raise NotFoundError(message="Trusted device not found.", code="device_not_found")

        if device.user_id != actor.id:
            if actor.role.name != "super_admin":
                raise PermissionDeniedError(message="Cannot revoke another user's device.", code="forbidden")
            if target_user and device.user_id != target_user.id:
                raise PermissionDeniedError(message="Device does not belong to target user.", code="forbidden")

        self.repository.revoke(device)
        trusted_device_session_revocation_service.revoke_device_sessions(
            device, actor=actor, ip_address=None
        )

        from apps.trusted_devices.models import TrustedDeviceEvent

        trusted_device_audit_service.record(
            user=device.user,
            event_type=TrustedDeviceEvent.EventType.DEVICE_REVOKED,
            device=device,
            metadata={"revoked_by": str(actor.uuid)},
        )
        return device

    def assign_university_managed(self, actor: User, device_uuid) -> TrustedDevice:
        if actor.role.name != Role.Name.SUPER_ADMIN:
            raise PermissionDeniedError(message="Only Super Admin can assign university devices.", code="forbidden")
        device = self.repository.get_by_uuid(device_uuid)
        if not device:
            raise NotFoundError(message="Trusted device not found.", code="device_not_found")

        from apps.trusted_devices.constants import DeviceType

        policy = trusted_device_policy_service.get_policy()
        device.device_type = DeviceType.UNIVERSITY_MANAGED
        device.expires_at = timezone.now() + timedelta(
            days=trusted_device_policy_service.expiration_days_for_device_type(DeviceType.UNIVERSITY_MANAGED)
        )
        device.save(update_fields=["device_type", "expires_at", "updated_at"])

        from apps.trusted_devices.services.risk_score_service import device_risk_score_service

        device_risk_score_service.adjust(device, -10.0, reason="university_assigned")

        trusted_device_audit_service.record(
            user=device.user,
            event_type=TrustedDeviceEvent.EventType.UNIVERSITY_DEVICE_ASSIGNED,
            device=device,
            metadata={"assigned_by": str(actor.uuid)},
        )
        return device

    def remove_device(self, actor: User, device_uuid) -> None:
        device = self.get_device(actor, device_uuid)
        self.repository.delete(device)

    def identify_current(
        self,
        user: User,
        raw_token: str | None,
        context: DeviceContext,
    ) -> TrustedDevice | None:
        return self.validate_token(user, raw_token, context)


trusted_device_service = TrustedDeviceService()
