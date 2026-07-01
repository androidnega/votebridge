import hashlib
import re
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    """Election and security activity audit trail."""

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILED = "login_failed", "Login Failed"
        LOGOUT = "logout", "Logout"
        OTP_SENT = "otp_sent", "OTP Sent"
        OTP_VERIFIED = "otp_verified", "OTP Verified"
        OTP_FAILED = "otp_failed", "OTP Failed"
        MFA_REQUIRED = "mfa_required", "MFA Required"
        MFA_COMPLETED = "mfa_completed", "MFA Completed"
        SESSION_REVOKED = "session_revoked", "Session Revoked"
        TOKEN_REFRESH = "token_refresh", "Token Refresh"
        ELECTION_ACCESSED = "election_accessed", "Election Accessed"
        ELECTION_CREATED = "election_created", "Election Created"
        ELECTION_UPDATED = "election_updated", "Election Updated"
        ELECTION_DELETED = "election_deleted", "Election Deleted"
        ELECTION_STATUS_CHANGED = "election_status_changed", "Election Status Changed"
        BALLOT_VIEWED = "ballot_viewed", "Ballot Viewed"
        VOTE_CAST = "vote_cast", "Vote Cast"
        VOTE_VERIFIED = "vote_verified", "Vote Verified"
        VOTE_CONFIRMATION_VIEWED = "vote_confirmation_viewed", "Vote Confirmation Viewed"
        SVT_ISSUED = "svt_issued", "SVT Issued"
        SVT_VALIDATED = "svt_validated", "SVT Validated"
        BALLOT_STARTED = "ballot_started", "Ballot Started"
        BALLOT_SUBMITTED = "ballot_submitted", "Ballot Submitted"
        SVT_CONSUMED = "svt_consumed", "SVT Consumed"
        SVT_REVOKED = "svt_revoked", "SVT Revoked"
        SVT_REISSUED = "svt_reissued", "SVT Reissued"
        SVT_VOTE_VERIFIED = "svt_vote_verified", "SVT Vote Verified"
        ADMIN_ACTION = "admin_action", "Admin Action"

    audit_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="audit_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        db_column="user_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        db_column="election_id",
    )
    device_log = models.ForeignKey(
        "security.DeviceLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        db_column="device_log_id",
    )
    location_log = models.ForeignKey(
        "security.LocationLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        db_column="location_log_id",
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices, db_column="event_type", db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_column="ip_address")
    user_agent = models.TextField(blank=True, db_column="user_agent")
    metadata = models.JSONField(default=dict, blank=True, db_column="metadata")
    timestamp = models.DateTimeField(default=timezone.now, db_column="timestamp", db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "event_type"]),
            models.Index(fields=["election", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.timestamp})"


class DeviceLog(models.Model):
    """Tracked client device for election monitoring."""

    device_log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="device_log_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_logs",
        db_column="user_id",
    )
    browser_fingerprint = models.CharField(max_length=128, db_column="browser_fingerprint", db_index=True)
    device_type = models.CharField(max_length=20, db_column="device_type")
    operating_system = models.CharField(max_length=50, db_column="operating_system")
    user_agent = models.TextField(db_column="user_agent")
    last_seen_at = models.DateTimeField(default=timezone.now, db_column="last_seen_at", db_index=True)

    class Meta:
        db_table = "device_logs"
        ordering = ["-last_seen_at"]
        indexes = [
            models.Index(fields=["browser_fingerprint", "user"]),
        ]

    def __str__(self):
        return f"Device {self.device_log_id} ({self.device_type})"


class LocationLog(models.Model):
    """Tracked IP geolocation for election monitoring."""

    location_log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="location_log_id",
    )
    ip_address = models.GenericIPAddressField(unique=True, db_column="ip_address")
    country = models.CharField(max_length=100, blank=True, db_column="country")
    region = models.CharField(max_length=100, blank=True, db_column="region")
    city = models.CharField(max_length=100, blank=True, db_column="city")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        db_column="latitude",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        db_column="longitude",
    )
    last_seen_at = models.DateTimeField(default=timezone.now, db_column="last_seen_at", db_index=True)

    class Meta:
        db_table = "location_logs"
        ordering = ["-last_seen_at"]

    def __str__(self):
        return f"{self.ip_address} ({self.city or self.country or 'Unknown'})"


_DEVICE_TYPE_PATTERN = re.compile(r"mobile|android|iphone|ipod", re.I)
_TABLET_PATTERN = re.compile(r"tablet|ipad", re.I)
_OS_PATTERNS = (
    ("Windows", re.compile(r"windows", re.I)),
    ("macOS", re.compile(r"mac os|macintosh", re.I)),
    ("iOS", re.compile(r"iphone|ipad|ipod", re.I)),
    ("Android", re.compile(r"android", re.I)),
    ("Linux", re.compile(r"linux", re.I)),
)


def parse_device_type(user_agent: str) -> str:
    if _TABLET_PATTERN.search(user_agent):
        return "tablet"
    if _DEVICE_TYPE_PATTERN.search(user_agent):
        return "mobile"
    return "desktop"


def parse_operating_system(user_agent: str) -> str:
    for name, pattern in _OS_PATTERNS:
        if pattern.search(user_agent):
            return name
    return "Unknown"


class SVTToken(models.Model):
    """Secure Voting Token — one-time authorization for submitting an election ballot."""

    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        VALIDATED = "validated", "Validated"
        USED = "used", "Used"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    svt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="svt_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="svt_tokens",
        db_column="user_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="svt_tokens",
        db_column="election_id",
    )
    token_code = models.CharField(max_length=128, db_column="token_code", unique=True)
    issued_at = models.DateTimeField(default=timezone.now, db_column="issued_at")
    expires_at = models.DateTimeField(db_column="expires_at")
    used_at = models.DateTimeField(null=True, blank=True, db_column="used_at")
    validated_at = models.DateTimeField(null=True, blank=True, db_column="validated_at")
    validation_attempts = models.PositiveSmallIntegerField(default=0, db_column="validation_attempts")
    last_resent_at = models.DateTimeField(null=True, blank=True, db_column="last_resent_at")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ISSUED,
        db_column="status",
        db_index=True,
    )

    class Meta:
        db_table = "svt_tokens"
        ordering = ["-issued_at"]
        verbose_name = "SVT token"
        verbose_name_plural = "SVT tokens"
        indexes = [
            models.Index(fields=["election", "user", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"SVT {self.svt_id} ({self.status})"

    @staticmethod
    def generate_token_code() -> str:
        """Phase 56 — six-digit numeric Secure Voting Token."""
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def hash_token_code(token_code: str) -> str:
        return hashlib.sha256(token_code.encode("utf-8")).hexdigest()

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def mark_expired_if_needed(self) -> bool:
        if self.status == self.Status.ISSUED and self.is_expired:
            self.status = self.Status.EXPIRED
            self.save(update_fields=["status"])
            return True
        return False
