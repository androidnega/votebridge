from django.contrib import admin

from apps.fraud.models import FraudCase, SecurityAlert


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ("alert_id", "alert_type", "status", "user", "election", "created_at")
    list_filter = ("alert_type", "status")
    search_fields = ("title", "description", "user__email")
    readonly_fields = (
        "alert_id",
        "alert_type",
        "status",
        "user",
        "election",
        "device_log",
        "location_log",
        "title",
        "description",
        "metadata",
        "created_at",
        "reviewed_at",
        "reviewed_by",
        "resolved_at",
        "resolved_by",
        "escalated_at",
        "escalated_by",
    )

    def has_add_permission(self, request):
        return False


@admin.register(FraudCase)
class FraudCaseAdmin(admin.ModelAdmin):
    list_display = (
        "fraud_case_id",
        "severity",
        "status",
        "risk_score",
        "user",
        "election",
        "created_at",
    )
    list_filter = ("severity", "status")
    search_fields = ("fraud_case_id", "user__email", "related_alert__title")
    readonly_fields = (
        "fraud_case_id",
        "election",
        "user",
        "related_alert",
        "risk_score",
        "severity",
        "status",
        "investigation_notes",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
