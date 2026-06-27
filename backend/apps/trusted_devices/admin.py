from django.contrib import admin

from apps.trusted_devices.models import TrustedDevice, TrustedDeviceEvent


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "device_name", "is_trusted", "is_revoked", "last_seen", "expires_at")
    list_filter = ("is_trusted", "is_revoked", "operating_system", "browser_name")
    search_fields = ("user__email", "device_name", "last_ip")
    readonly_fields = ("uuid", "device_token_hash", "created_at", "updated_at")


@admin.register(TrustedDeviceEvent)
class TrustedDeviceEventAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "event_type", "decision", "risk_score", "country", "created_at")
    list_filter = ("event_type", "decision")
    readonly_fields = ("uuid", "created_at")
