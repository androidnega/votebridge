from django.contrib import admin

from apps.biometrics.models import BiometricProfile, BiometricVerificationLog


@admin.register(BiometricProfile)
class BiometricProfileAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "quality_score", "is_active", "last_verified_at", "created_at")
    list_filter = ("is_active", "embedding_algorithm", "model_version")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("uuid", "encrypted_embedding", "created_at", "updated_at")


@admin.register(BiometricVerificationLog)
class BiometricVerificationLogAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "event_type", "outcome", "confidence", "created_at")
    list_filter = ("event_type", "outcome")
    search_fields = ("user__email", "challenge_type")
    readonly_fields = ("uuid", "created_at")
