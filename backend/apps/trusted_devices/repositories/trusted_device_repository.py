from datetime import timedelta

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent, TrustedDeviceLoginHistory


class TrustedDeviceRepository:
    def get_queryset(self) -> QuerySet[TrustedDevice]:
        return TrustedDevice.objects.select_related("user")

    def get_by_uuid(self, device_uuid) -> TrustedDevice | None:
        return self.get_queryset().filter(uuid=device_uuid).first()

    def get_by_token_hash(self, user: User, token_hash: str) -> TrustedDevice | None:
        return (
            self.get_queryset()
            .filter(user=user, device_token_hash=token_hash, is_revoked=False)
            .first()
        )

    def list_for_user(self, user: User) -> QuerySet[TrustedDevice]:
        return self.get_queryset().filter(user=user).order_by("-last_seen")

    def list_active_for_user(self, user: User) -> QuerySet[TrustedDevice]:
        now = timezone.now()
        return self.get_queryset().filter(
            user=user,
            is_trusted=True,
            is_revoked=False,
            expires_at__gt=now,
        )

    def count_active_for_user(self, user: User) -> int:
        return self.list_active_for_user(user).count()

    def create(self, **kwargs) -> TrustedDevice:
        return TrustedDevice.objects.create(**kwargs)

    def update(self, device: TrustedDevice, **kwargs) -> TrustedDevice:
        for key, value in kwargs.items():
            setattr(device, key, value)
        device.save()
        return device

    def revoke(self, device: TrustedDevice) -> TrustedDevice:
        from apps.trusted_devices.constants import TrustLevel

        device.is_revoked = True
        device.is_trusted = False
        device.trust_level = TrustLevel.REVOKED
        device.save(update_fields=["is_revoked", "is_trusted", "trust_level", "updated_at"])
        return device

    def delete(self, device: TrustedDevice) -> None:
        device.delete()

    def find_by_fingerprint(self, user: User, fingerprint: str) -> TrustedDevice | None:
        return (
            self.get_queryset()
            .filter(user=user, browser_fingerprint=fingerprint, is_revoked=False)
            .order_by("-last_seen")
            .first()
        )

    def list_expired(self) -> QuerySet[TrustedDevice]:
        now = timezone.now()
        return self.get_queryset().filter(
            expires_at__lte=now,
            is_revoked=False,
        )


class TrustedDeviceEventRepository:
    def create(self, **kwargs) -> TrustedDeviceEvent:
        return TrustedDeviceEvent.objects.create(**kwargs)

    def list_for_user(self, user: User, *, limit: int = 50) -> QuerySet[TrustedDeviceEvent]:
        return TrustedDeviceEvent.objects.filter(user=user).order_by("-created_at")[:limit]


class TrustedDeviceLoginHistoryRepository:
    def create(self, **kwargs) -> TrustedDeviceLoginHistory:
        return TrustedDeviceLoginHistory.objects.create(**kwargs)

    def list_for_device(self, device: TrustedDevice, *, limit: int = 20) -> QuerySet[TrustedDeviceLoginHistory]:
        return TrustedDeviceLoginHistory.objects.filter(device=device).order_by("-logged_in_at")[:limit]

    def get_last_for_user(self, user: User) -> TrustedDeviceLoginHistory | None:
        return (
            TrustedDeviceLoginHistory.objects.filter(user=user)
            .order_by("-logged_in_at")
            .first()
        )
