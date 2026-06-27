from django.contrib import admin

from apps.accounts.models import MFALog, OTPRequest, Role, Session, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "name")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("name",)


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "purpose",
        "channel",
        "is_verified",
        "attempts",
        "expires_at",
        "created_at",
    )
    list_filter = ("purpose", "channel", "is_verified")
    search_fields = ("user__email", "user__index_number")
    readonly_fields = ("uuid", "otp_hash", "created_at", "verified_at")
    ordering = ("-created_at",)


@admin.register(MFALog)
class MFALogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "user", "ip_address", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("user__email", "ip_address", "event_type")
    readonly_fields = ("uuid", "created_at")
    ordering = ("-created_at",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_active",
        "ip_address",
        "expires_at",
        "last_activity_at",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email", "refresh_token_jti", "ip_address")
    readonly_fields = ("uuid", "refresh_token_jti", "created_at", "revoked_at")
    ordering = ("-created_at",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "index_number",
        "student_id",
        "is_active",
        "is_verified",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_verified", "is_staff")
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "index_number",
        "student_id",
        "phone_number",
    )
    readonly_fields = ("uuid", "created_at", "updated_at", "last_login", "date_joined")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "index_number",
                    "student_id",
                ),
            },
        ),
        ("Role & Status", {"fields": ("role", "is_active", "is_verified", "is_staff")}),
        (
            "Permissions",
            {"fields": ("is_superuser", "groups", "user_permissions")},
        ),
        (
            "Metadata",
            {
                "fields": (
                    "uuid",
                    "username",
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "role",
                    "index_number",
                    "student_id",
                    "phone_number",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")
