from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.accounts.models import MFALog, OTPRequest, Session


class OTPRequestRepository:
    def get_queryset(self):
        return OTPRequest.objects.select_related("user").all()

    def get_by_uuid(self, uuid):
        return self.get_queryset().filter(uuid=uuid).first()

    def create(self, **data) -> OTPRequest:
        return OTPRequest.objects.create(**data)

    def update(self, otp_request: OTPRequest, **data) -> OTPRequest:
        for field, value in data.items():
            setattr(otp_request, field, value)
        otp_request.save()
        return otp_request

    def invalidate_active_for_user(self, user, purpose: str) -> None:
        OTPRequest.objects.filter(
            user=user,
            purpose=purpose,
            is_verified=False,
            expires_at__gt=timezone.now(),
        ).update(expires_at=timezone.now())

    def count_recent_for_user(self, user, minutes: int = 15) -> int:
        since = timezone.now() - timedelta(minutes=minutes)
        return OTPRequest.objects.filter(user=user, created_at__gte=since).count()


class MFALogRepository:
    def get_queryset(self):
        return MFALog.objects.select_related("user").all()

    def create(self, **data) -> MFALog:
        return MFALog.objects.create(**data)

    def list_for_user(self, user, limit: int = 50):
        return self.get_queryset().filter(user=user).order_by("-created_at")[:limit]

    def list_recent(self, user=None, limit: int = 100):
        queryset = self.get_queryset()
        if user:
            queryset = queryset.filter(user=user)
        return queryset.order_by("-created_at")[:limit]


class SessionRepository:
    def get_queryset(self):
        return Session.objects.select_related("user").all()

    def get_by_uuid(self, uuid):
        return self.get_queryset().filter(uuid=uuid).first()

    def get_by_jti(self, jti: str):
        return self.get_queryset().filter(refresh_token_jti=jti).first()

    def create(self, **data) -> Session:
        return Session.objects.create(**data)

    def update(self, session: Session, **data) -> Session:
        for field, value in data.items():
            setattr(session, field, value)
        session.save()
        return session

    def list_active_for_user(self, user):
        return self.get_queryset().filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now(),
        )

    def revoke(self, session: Session) -> Session:
        session.is_active = False
        session.revoked_at = timezone.now()
        session.save(update_fields=["is_active", "revoked_at"])
        return session

    def revoke_all_for_user(self, user, exclude_jti: str | None = None) -> int:
        queryset = self.get_queryset().filter(user=user, is_active=True)
        if exclude_jti:
            queryset = queryset.exclude(refresh_token_jti=exclude_jti)
        return queryset.update(
            is_active=False,
            revoked_at=timezone.now(),
        )

    def get_session_lifetime_days(self) -> int:
        return int(getattr(settings, "AUTH_SESSION_LIFETIME_DAYS", 7))
