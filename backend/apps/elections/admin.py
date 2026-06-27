from django.contrib import admin

from apps.elections.models import Election, Position, VoterEligibility, VotingChannel


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "election_type",
        "status",
        "start_date",
        "end_date",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "election_type", "allow_web_voting", "allow_ussd_voting")
    search_fields = ("title", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)
    date_hierarchy = "start_date"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "election",
        "max_votes_allowed",
        "display_order",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "election")
    search_fields = ("title", "description", "election__title")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("election", "display_order", "title")


@admin.register(VoterEligibility)
class VoterEligibilityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "election",
        "is_eligible",
        "verified_by",
        "verified_at",
        "created_at",
    )
    list_filter = ("is_eligible", "election")
    search_fields = (
        "user__email",
        "user__index_number",
        "election__title",
        "eligibility_reason",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(VotingChannel)
class VotingChannelAdmin(admin.ModelAdmin):
    list_display = ("channel_name", "is_active", "created_at")
    list_filter = ("is_active", "channel_name")
    readonly_fields = ("uuid", "created_at")
    ordering = ("channel_name",)
