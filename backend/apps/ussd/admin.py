from django.contrib import admin

from apps.ussd.models import USSDRequestLog, USSDSession


@admin.register(USSDSession)
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "msisdn", "status", "current_step", "completed_vote", "started_at")
    list_filter = ("status", "completed_vote")
    search_fields = ("session_id", "msisdn")


@admin.register(USSDRequestLog)
class USSDRequestLogAdmin(admin.ModelAdmin):
    list_display = ("carrier_session_id", "msisdn", "step_after", "outcome", "duration_ms", "created_at")
    list_filter = ("outcome",)
