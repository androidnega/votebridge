from django.contrib import admin

from apps.candidates.models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "election",
        "position",
        "department",
        "status",
        "created_at",
    )
    list_filter = ("status", "election", "position")
    search_fields = ("full_name", "position__title", "department", "election__title")
    readonly_fields = ("uuid", "created_at")
    ordering = ("-created_at",)
