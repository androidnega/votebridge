from django.db.models import QuerySet

from apps.accounts.models import Role, User
from apps.biometrics.constants import ENROLLMENT_IMAGE_COUNT, PRIVILEGED_ROLES, PRIVILEGED_USERNAMES
from apps.biometrics.models import BiometricProfile, BiometricVerificationLog


class BiometricProfileRepository:
    def get_queryset(self) -> QuerySet[BiometricProfile]:
        return BiometricProfile.objects.select_related("user", "user__role")

    def get_by_user(self, user: User) -> BiometricProfile | None:
        return self.get_queryset().filter(user=user).first()

    def get_by_uuid(self, profile_uuid) -> BiometricProfile | None:
        return self.get_queryset().filter(uuid=profile_uuid).first()

    def create(self, **kwargs) -> BiometricProfile:
        return BiometricProfile.objects.create(**kwargs)

    def update(self, profile: BiometricProfile, **kwargs) -> BiometricProfile:
        for key, value in kwargs.items():
            setattr(profile, key, value)
        profile.save()
        return profile

    def delete_for_user(self, user: User) -> int:
        deleted, _ = BiometricProfile.objects.filter(user=user).delete()
        return deleted


class BiometricVerificationLogRepository:
    def get_queryset(self) -> QuerySet[BiometricVerificationLog]:
        return BiometricVerificationLog.objects.select_related("user")

    def create(self, **kwargs) -> BiometricVerificationLog:
        return BiometricVerificationLog.objects.create(**kwargs)

    def list_for_user(self, user: User, *, limit: int = 50) -> QuerySet[BiometricVerificationLog]:
        return self.get_queryset().filter(user=user).order_by("-created_at")[:limit]

    def list_recent(self, *, limit: int = 100) -> QuerySet[BiometricVerificationLog]:
        return self.get_queryset().order_by("-created_at")[:limit]

    def search(
        self,
        *,
        user: User | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> QuerySet[BiometricVerificationLog]:
        qs = self.get_queryset()
        if user:
            qs = qs.filter(user=user)
        if event_type:
            qs = qs.filter(event_type=event_type)
        return qs.order_by("-created_at")[:limit]
