import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class BiometricProfile(models.Model):
    """Encrypted face embedding for privileged users — never store raw images."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="biometric_profile",
    )
    encrypted_embedding = models.TextField()
    embedding_algorithm = models.CharField(max_length=32, default="arcface")
    model_version = models.CharField(max_length=32, default="arcface_v1")
    quality_score = models.FloatField(default=0.0)
    enrollment_images_count = models.PositiveSmallIntegerField(default=0)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "biometrics_profile"
        ordering = ["-created_at"]
        verbose_name = "biometric profile"
        verbose_name_plural = "biometric profiles"

    def __str__(self):
        return f"BiometricProfile({self.user_id})"

    @property
    def is_locked(self) -> bool:
        if not self.locked_until:
            return False
        return self.locked_until > timezone.now()


class BiometricVerificationLog(models.Model):
    """Audit trail for enrollment and verification events."""

    class EventType(models.TextChoices):
        ENROLLMENT = "enrollment", "Enrollment"
        VERIFICATION_PASSED = "verification_passed", "Verification Passed"
        VERIFICATION_FAILED = "verification_failed", "Verification Failed"
        CHALLENGE_FAILED = "challenge_failed", "Challenge Failed"
        SPOOF_ATTEMPT = "spoof_attempt", "Spoof Attempt"
        ACCOUNT_LOCKED = "account_locked", "Account Locked"
        STRONGROOM_VERIFICATION = "strongroom_verification", "Strongroom Verification"
        STEP_UP = "step_up", "Step-Up Verification"

    class Outcome(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"
        BLOCKED = "blocked", "Blocked"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="biometric_verification_logs",
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices, db_index=True)
    outcome = models.CharField(max_length=16, choices=Outcome.choices, default=Outcome.FAILURE)
    challenge_type = models.CharField(max_length=32, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    liveness_score = models.FloatField(null=True, blank=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    model_version = models.CharField(max_length=32, blank=True)
    device_fingerprint = models.CharField(max_length=128, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "biometrics_verification_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "event_type"]),
            models.Index(fields=["created_at", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.created_at})"
