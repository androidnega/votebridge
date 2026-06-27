import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class SecurityAlert(models.Model):
    """Suspicious activity alert for admin review."""

    class AlertType(models.TextChoices):
        DUPLICATE_DEVICE = "duplicate_device", "Duplicate Device"
        DUPLICATE_LOCATION = "duplicate_location", "Duplicate Location"
        EXCESSIVE_LOGIN_ATTEMPTS = "excessive_login_attempts", "Excessive Login Attempts"
        EXCESSIVE_SVT_REQUESTS = "excessive_svt_requests", "Excessive SVT Requests"
        SUSPICIOUS_VOTING_PATTERN = "suspicious_voting_pattern", "Suspicious Voting Pattern"
        MULTIPLE_ACCOUNTS_SAME_DEVICE = "multiple_accounts_same_device", "Multiple Accounts Same Device"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWING = "reviewing", "Reviewing"
        RESOLVED = "resolved", "Resolved"
        ESCALATED = "escalated", "Escalated"

    alert_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="alert_id",
    )
    alert_type = models.CharField(max_length=40, choices=AlertType.choices, db_column="alert_type", db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_column="status",
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_alerts",
        db_column="user_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_alerts",
        db_column="election_id",
    )
    device_log = models.ForeignKey(
        "security.DeviceLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_alerts",
        db_column="device_log_id",
    )
    location_log = models.ForeignKey(
        "security.LocationLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_alerts",
        db_column="location_log_id",
    )
    title = models.CharField(max_length=200, db_column="title")
    description = models.TextField(db_column="description")
    metadata = models.JSONField(default=dict, blank=True, db_column="metadata")
    created_at = models.DateTimeField(default=timezone.now, db_column="created_at", db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True, db_column="reviewed_at")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_alerts",
        db_column="reviewed_by_id",
    )
    resolved_at = models.DateTimeField(null=True, blank=True, db_column="resolved_at")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
        db_column="resolved_by_id",
    )
    escalated_at = models.DateTimeField(null=True, blank=True, db_column="escalated_at")
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalated_alerts",
        db_column="escalated_by_id",
    )

    class Meta:
        db_table = "security_alerts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alert_type", "status"]),
            models.Index(fields=["election", "status"]),
        ]

    def __str__(self):
        return f"{self.alert_type} ({self.status})"


class FraudCase(models.Model):
    """Fraud investigation case linked to a security alert."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"
        ESCALATED = "escalated", "Escalated"

    fraud_case_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="fraud_case_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_cases",
        db_column="election_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_cases",
        db_column="user_id",
    )
    related_alert = models.ForeignKey(
        SecurityAlert,
        on_delete=models.PROTECT,
        related_name="fraud_cases",
        db_column="related_alert_id",
    )
    risk_score = models.PositiveSmallIntegerField(default=0, db_column="risk_score")
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.LOW,
        db_column="severity",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_column="status",
        db_index=True,
    )
    investigation_notes = models.TextField(blank=True, db_column="investigation_notes")
    created_at = models.DateTimeField(default=timezone.now, db_column="created_at", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_column="updated_at")

    class Meta:
        db_table = "fraud_cases"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["election", "status"]),
            models.Index(fields=["severity", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["related_alert"],
                name="fraud_unique_case_per_alert",
            ),
        ]

    def __str__(self):
        return f"FraudCase {self.fraud_case_id} ({self.severity}/{self.status})"
