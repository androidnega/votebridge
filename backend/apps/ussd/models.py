import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class USSDSession(models.Model):
    """Stateful USSD session for menu navigation and voting progress."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"
        EXPIRED = "expired", "Expired"
        FAILED = "failed", "Failed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    session_id = models.CharField(max_length=120, unique=True, db_index=True)
    msisdn = models.CharField(max_length=20, db_index=True)
    service_code = models.CharField(max_length=40, blank=True)
    network = models.CharField(max_length=40, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ussd_sessions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    current_step = models.CharField(max_length=60, default="WELCOME", db_index=True)
    state_data = models.JSONField(default=dict, blank=True)
    request_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_activity_at = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    completed_vote = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "ussd_session"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["status", "last_activity_at"]),
            models.Index(fields=["msisdn", "status"]),
        ]

    def __str__(self):
        return f"USSD {self.session_id} ({self.status})"


class USSDRequestLog(models.Model):
    """Audit log for every USSD callback request and response."""

    class Outcome(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        TIMEOUT = "timeout", "Timeout"
        INVALID = "invalid", "Invalid"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    session = models.ForeignKey(
        USSDSession,
        on_delete=models.CASCADE,
        related_name="request_logs",
        null=True,
        blank=True,
    )
    carrier_session_id = models.CharField(max_length=120, db_index=True)
    msisdn = models.CharField(max_length=20, db_index=True)
    raw_input = models.TextField(blank=True)
    parsed_inputs = models.JSONField(default=list, blank=True)
    step_before = models.CharField(max_length=60, blank=True)
    step_after = models.CharField(max_length=60, blank=True)
    response_message = models.TextField(blank=True)
    continue_session = models.BooleanField(default=True)
    outcome = models.CharField(
        max_length=20,
        choices=Outcome.choices,
        default=Outcome.SUCCESS,
        db_index=True,
    )
    error_message = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    provider_user_id = models.CharField(max_length=120, blank=True)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    http_status = models.PositiveSmallIntegerField(default=200)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "ussd_request_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["outcome", "created_at"]),
            models.Index(fields=["msisdn", "created_at"]),
        ]

    def __str__(self):
        return f"USSD log {self.session_id} @ {self.created_at}"
