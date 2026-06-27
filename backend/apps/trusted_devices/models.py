import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


from apps.trusted_devices.constants import DeviceType, TrustLevel


class TrustedDevice(models.Model):
    """Registered trusted browser/device for privileged administrators."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trusted_devices",
    )
    device_name = models.CharField(max_length=128, default="Trusted Device")
    device_type = models.CharField(
        max_length=24,
        choices=DeviceType.CHOICES,
        default=DeviceType.PERSONAL,
        db_index=True,
    )
    trust_level = models.CharField(
        max_length=16,
        choices=TrustLevel.CHOICES,
        default=TrustLevel.MEDIUM,
        db_index=True,
    )
    device_token_hash = models.CharField(max_length=128, db_index=True)
    browser_fingerprint = models.CharField(max_length=256, db_index=True)
    operating_system = models.CharField(max_length=64, blank=True)
    browser_name = models.CharField(max_length=64, blank=True)
    browser_version = models.CharField(max_length=32, blank=True)
    platform = models.CharField(max_length=64, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    language = models.CharField(max_length=32, blank=True)
    screen_resolution = models.CharField(max_length=32, blank=True)
    first_ip = models.GenericIPAddressField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    first_country = models.CharField(max_length=100, blank=True)
    last_country = models.CharField(max_length=100, blank=True)
    first_city = models.CharField(max_length=100, blank=True)
    last_city = models.CharField(max_length=100, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    previous_login_at = models.DateTimeField(null=True, blank=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    last_biometric = models.DateTimeField(null=True, blank=True)
    risk_score = models.FloatField(default=0.0)
    is_trusted = models.BooleanField(default=True, db_index=True)
    is_revoked = models.BooleanField(default=False, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trusted_device"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["user", "is_trusted", "is_revoked"]),
            models.Index(fields=["user", "device_token_hash"]),
        ]
        verbose_name = "trusted device"
        verbose_name_plural = "trusted devices"

    def __str__(self):
        return f"{self.device_name} ({self.user_id})"

    @property
    def is_valid(self) -> bool:
        if self.is_revoked or not self.is_trusted or self.trust_level == TrustLevel.REVOKED:
            return False
        return self.expires_at > timezone.now()


class TrustedDeviceLoginHistory(models.Model):
    """Per-device login audit trail for administrator trust review."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trusted_device_login_history",
    )
    device = models.ForeignKey(
        TrustedDevice,
        on_delete=models.CASCADE,
        related_name="login_history",
    )
    logged_in_at = models.DateTimeField(db_index=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    browser_name = models.CharField(max_length=64, blank=True)
    operating_system = models.CharField(max_length=64, blank=True)
    authentication_method = models.CharField(max_length=32, blank=True)
    risk_score = models.FloatField(default=0.0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trusted_device_login_history"
        ordering = ["-logged_in_at"]
        indexes = [
            models.Index(fields=["device", "logged_in_at"]),
            models.Index(fields=["user", "logged_in_at"]),
        ]


class TrustedDeviceEvent(models.Model):
    """Audit log for trusted device lifecycle and risk decisions."""

    class EventType(models.TextChoices):
        DEVICE_REGISTERED = "device_registered", "Device Registered"
        DEVICE_REVOKED = "device_revoked", "Device Revoked"
        DEVICE_EXPIRED = "device_expired", "Device Expired"
        TRUSTED_LOGIN = "trusted_login", "Trusted Login"
        HIGH_RISK_LOGIN = "high_risk_login", "High Risk Login"
        NEW_COUNTRY_LOGIN = "new_country_login", "New Country Login"
        BIOMETRIC_TRIGGERED = "biometric_triggered", "Biometric Triggered"
        DEVICE_RENAMED = "device_renamed", "Device Renamed"
        TRUST_LEVEL_CHANGED = "trust_level_changed", "Trust Level Changed"
        RISK_SCORE_CHANGED = "risk_score_changed", "Risk Score Changed"
        IMPOSSIBLE_TRAVEL = "impossible_travel", "Impossible Travel"
        DEVICE_RENEWED = "device_renewed", "Device Renewed"
        SESSION_REVOKED = "session_revoked", "Session Revoked"
        UNIVERSITY_DEVICE_ASSIGNED = "university_device_assigned", "University Device Assigned"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trusted_device_events",
    )
    device = models.ForeignKey(
        TrustedDevice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices, db_index=True)
    decision = models.CharField(max_length=24, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    browser_name = models.CharField(max_length=64, blank=True)
    operating_system = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "trusted_device_event"
        ordering = ["-created_at"]
