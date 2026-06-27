from django.contrib import admin

from apps.notifications.models import (
    CommunicationProvider,
    DeliveryLog,
    InAppNotification,
    NotificationTemplate,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "channel", "is_active")
    search_fields = ("code", "name")
    list_filter = ("channel", "is_active")


@admin.register(CommunicationProvider)
class CommunicationProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "provider_type", "is_active", "connection_status", "last_success_at")
    list_filter = ("provider_type", "is_active", "connection_status")


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("uuid", "channel", "recipient", "status", "template_code", "created_at")
    list_filter = ("channel", "status")
    search_fields = ("recipient", "template_code")


@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "is_archived", "created_at")
    list_filter = ("is_read", "is_archived", "category")
