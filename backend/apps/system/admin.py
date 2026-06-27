from django.contrib import admin

from apps.system.models import (
    BackupRecord,
    FeatureFlag,
    InstitutionProfile,
    MaintenanceState,
    SettingRevision,
    SystemSetting,
)


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    list_display = ("institution_name", "short_name", "updated_at")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "category", "version", "is_sensitive", "updated_at")
    list_filter = ("category", "is_sensitive")
    search_fields = ("key",)


@admin.register(SettingRevision)
class SettingRevisionAdmin(admin.ModelAdmin):
    list_display = ("setting_key", "version", "changed_by", "created_at")
    list_filter = ("category",)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "enabled", "last_changed_at")
    list_filter = ("enabled",)


@admin.register(MaintenanceState)
class MaintenanceStateAdmin(admin.ModelAdmin):
    list_display = ("is_enabled", "read_only_mode", "updated_at")


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ("filename", "status", "backup_type", "created_at")
    list_filter = ("status", "backup_type")
