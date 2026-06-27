from django.db.models import QuerySet

from apps.notifications.models import CommunicationProvider
from apps.system.models import (
    BackupRecord,
    FeatureFlag,
    InstitutionProfile,
    MaintenanceState,
    SettingRevision,
    SystemSetting,
)


class InstitutionRepository:
    def get_profile(self) -> InstitutionProfile | None:
        return InstitutionProfile.objects.first()

    def get_or_create_profile(self) -> InstitutionProfile:
        profile = self.get_profile()
        if profile:
            return profile
        return InstitutionProfile.objects.create()

    def save_profile(self, profile: InstitutionProfile, **fields) -> InstitutionProfile:
        for key, value in fields.items():
            setattr(profile, key, value)
        profile.save()
        return profile


class SystemSettingRepository:
    def get_queryset(self) -> QuerySet[SystemSetting]:
        return SystemSetting.objects.all()

    def get_by_key(self, key: str) -> SystemSetting | None:
        return self.get_queryset().filter(key=key).first()

    def list_by_category(self, category: str) -> list[SystemSetting]:
        return list(self.get_queryset().filter(category=category).order_by("key"))

    def list_public(self) -> list[SystemSetting]:
        return list(self.get_queryset().filter(is_public=True))

    def create(self, **kwargs) -> SystemSetting:
        return SystemSetting.objects.create(**kwargs)

    def save(self, setting: SystemSetting) -> SystemSetting:
        setting.save()
        return setting


class SettingRevisionRepository:
    def create(self, **kwargs) -> SettingRevision:
        return SettingRevision.objects.create(**kwargs)

    def list_for_key(self, key: str, limit: int = 20) -> list[SettingRevision]:
        return list(SettingRevision.objects.filter(setting_key=key).order_by("-created_at")[:limit])


class FeatureFlagRepository:
    def list_all(self) -> list[FeatureFlag]:
        return list(FeatureFlag.objects.all().order_by("name"))

    def get_by_key(self, key: str) -> FeatureFlag | None:
        return FeatureFlag.objects.filter(key=key).first()

    def save(self, flag: FeatureFlag) -> FeatureFlag:
        flag.save()
        return flag


class MaintenanceRepository:
    def get_state(self) -> MaintenanceState | None:
        return MaintenanceState.objects.first()

    def get_or_create_state(self) -> MaintenanceState:
        state = self.get_state()
        if state:
            return state
        return MaintenanceState.objects.create()

    def save(self, state: MaintenanceState) -> MaintenanceState:
        state.save()
        return state


class BackupRepository:
    def list_all(self, limit: int = 50) -> list[BackupRecord]:
        return list(BackupRecord.objects.all()[:limit])

    def get_by_uuid(self, backup_uuid) -> BackupRecord | None:
        return BackupRecord.objects.filter(uuid=backup_uuid).first()

    def create(self, **kwargs) -> BackupRecord:
        return BackupRecord.objects.create(**kwargs)

    def save(self, record: BackupRecord) -> BackupRecord:
        record.save()
        return record


class ProviderRepository:
    """Read/write CommunicationProvider records for SCC."""

    def list_all(self) -> list[CommunicationProvider]:
        return list(CommunicationProvider.objects.all().order_by("provider_type", "name"))

    def get_by_uuid(self, provider_uuid) -> CommunicationProvider | None:
        return CommunicationProvider.objects.filter(uuid=provider_uuid).first()

    def save(self, provider: CommunicationProvider) -> CommunicationProvider:
        provider.save()
        return provider
