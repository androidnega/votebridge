from django.contrib import admin

from apps.fraud.models import SecurityAlert
from apps.security.models import AuditLog, DeviceLog, LocationLog, SVTToken


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("audit_id", "event_type", "user", "election", "ip_address", "timestamp")
    list_filter = ("event_type",)
    search_fields = ("audit_id", "user__email", "ip_address")
    readonly_fields = (
        "audit_id",
        "user",
        "election",
        "device_log",
        "location_log",
        "event_type",
        "ip_address",
        "user_agent",
        "metadata",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DeviceLog)
class DeviceLogAdmin(admin.ModelAdmin):
    list_display = ("device_log_id", "user", "device_type", "operating_system", "last_seen_at")
    list_filter = ("device_type", "operating_system")
    readonly_fields = (
        "device_log_id",
        "user",
        "browser_fingerprint",
        "device_type",
        "operating_system",
        "user_agent",
        "last_seen_at",
    )

    def has_add_permission(self, request):
        return False


@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ("location_log_id", "ip_address", "country", "city", "last_seen_at")
    list_filter = ("country",)
    readonly_fields = (
        "location_log_id",
        "ip_address",
        "country",
        "region",
        "city",
        "latitude",
        "longitude",
        "last_seen_at",
    )

    def has_add_permission(self, request):
        return False


@admin.register(SVTToken)
class SVTTokenAdmin(admin.ModelAdmin):
    list_display = (
        "svt_id",
        "user",
        "election",
        "status",
        "issued_at",
        "expires_at",
        "used_at",
    )
    list_filter = ("status", "election")
    search_fields = ("svt_id", "user__email", "user__index_number")
    readonly_fields = (
        "svt_id",
        "user",
        "election",
        "token_code",
        "issued_at",
        "expires_at",
        "used_at",
        "status",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
