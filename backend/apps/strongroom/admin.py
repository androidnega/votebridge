from django.contrib import admin

from apps.strongroom.models import (
    BallotSeal,
    CustodyRecord,
    ElectionSeal,
    IntegrityVerification,
)


@admin.register(BallotSeal)
class BallotSealAdmin(admin.ModelAdmin):
    list_display = ("uuid", "election", "user", "vote_count", "status", "sealed_at")
    list_filter = ("status",)
    readonly_fields = ("uuid", "seal_hash", "vote_references", "sealed_at")


@admin.register(ElectionSeal)
class ElectionSealAdmin(admin.ModelAdmin):
    list_display = ("election", "status", "sealed_at", "locked_at")
    list_filter = ("status",)
    readonly_fields = ("uuid", "election_seal_hash", "verification_hash", "ballot_seals_digest")


@admin.register(CustodyRecord)
class CustodyRecordAdmin(admin.ModelAdmin):
    list_display = ("action", "election", "actor", "timestamp")
    list_filter = ("action",)


@admin.register(IntegrityVerification)
class IntegrityVerificationAdmin(admin.ModelAdmin):
    list_display = ("election", "verification_type", "integrity_score", "is_valid", "verified_at")
    list_filter = ("verification_type", "is_valid")
