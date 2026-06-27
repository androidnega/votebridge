from django.contrib import admin

from apps.results.models import ElectionResult


@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = ("election", "status", "turnout_percentage", "total_votes_cast", "updated_at")
    list_filter = ("status",)
    search_fields = ("election__title",)
    readonly_fields = ("uuid", "result_hash", "standings", "integrity_report", "created_at", "updated_at")
