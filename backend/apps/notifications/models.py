import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationProvider(models.Model):
    """Registered communication provider (Arkesel SMS, SMTP email)."""

    class ProviderType(models.TextChoices):
        ARKESEL_SMS = "arkesel_sms", "Arkesel SMS"
        SMTP_EMAIL = "smtp_email", "SMTP Email"

    class ConnectionStatus(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        CONNECTED = "connected", "Connected"
        ERROR = "error", "Error"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    provider_type = models.CharField(max_length=30, choices=ProviderType.choices, db_index=True)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    connection_status = models.CharField(
        max_length=20,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.UNKNOWN,
    )
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications_provider"
        ordering = ["provider_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.provider_type})"


class NotificationTemplate(models.Model):
    """Reusable message template with placeholder support."""

    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        IN_APP = "in_app", "In-App"
        MULTI = "multi", "Multi-Channel"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.SlugField(max_length=80, unique=True, db_index=True)
    name = models.CharField(max_length=160)
    channel = models.CharField(max_length=20, choices=Channel.choices, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body_text = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    sms_body = models.TextField(blank=True)
    in_app_title = models.CharField(max_length=255, blank=True)
    in_app_body = models.TextField(blank=True)
    placeholders = models.JSONField(
        default=list,
        blank=True,
        help_text="List of supported placeholder keys, e.g. first_name, election_name.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications_template"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.channel})"


class DeliveryLog(models.Model):
    """Outbound message delivery record and queue entry."""

    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        IN_APP = "in_app", "In-App"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"
        CANCELLED = "cancelled", "Cancelled"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_logs",
    )
    recipient = models.CharField(max_length=255, db_index=True)
    channel = models.CharField(max_length=20, choices=Channel.choices, db_index=True)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_logs",
    )
    template_code = models.CharField(max_length=80, blank=True, db_index=True)
    provider = models.ForeignKey(
        CommunicationProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_logs",
    )
    provider_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    subject = models.CharField(max_length=255, blank=True)
    body_snapshot = models.TextField(blank=True)
    context_data = models.JSONField(default=dict, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=3)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "notifications_delivery_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "channel"]),
            models.Index(fields=["status", "next_retry_at"]),
        ]

    def __str__(self):
        return f"{self.channel} → {self.recipient} ({self.status})"


class InAppNotification(models.Model):
    """User notification centre entry."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="in_app_notifications",
    )
    delivery_log = models.ForeignKey(
        DeliveryLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="in_app_notifications",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    category = models.CharField(max_length=60, blank=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "notifications_in_app"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "is_deleted"]),
            models.Index(fields=["user", "is_archived", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.title} → {self.user_id}"
