from django.contrib import admin

from apps.voting.models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "vote_id",
        "election",
        "position",
        "candidate",
        "user",
        "channel",
        "timestamp",
    )
    list_filter = ("channel", "election", "timestamp")
    search_fields = (
        "vote_id",
        "vote_hash",
        "user__email",
        "candidate__full_name",
        "election__title",
    )
    readonly_fields = (
        "vote_id",
        "election",
        "position",
        "candidate",
        "user",
        "channel",
        "svt_id",
        "vote_hash",
        "timestamp",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
