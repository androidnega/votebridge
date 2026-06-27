import uuid

from django.conf import settings
from django.db import models


class InstitutionProfile(models.Model):
    """Single-tenant institution profile and public branding."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    institution_name = models.CharField(max_length=200, default="Takoradi Technical University")
    short_name = models.CharField(max_length=40, default="TTU")
    logo = models.ImageField(upload_to="institution/logos/", blank=True, null=True)
    logo_url = models.URLField(blank=True)
    favicon = models.ImageField(upload_to="institution/favicons/", blank=True, null=True)
    favicon_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default="#1E5F46")
    secondary_color = models.CharField(max_length=7, default="#334155")
    academic_year = models.CharField(max_length=20, blank=True, default="2024/2025")
    campus = models.CharField(max_length=120, blank=True, default="Main Campus")
    contact_email = models.EmailField(blank=True, default="info@ttu.edu.gh")
    contact_phone = models.CharField(max_length=30, blank=True)
    election_office_name = models.CharField(max_length=160, blank=True, default="Electoral Commission Office")
    election_office_email = models.EmailField(blank=True, default="elections@ttu.edu.gh")
    election_office_phone = models.CharField(max_length=30, blank=True)
    footer_text = models.TextField(blank=True)
    public_urls = models.JSONField(default=dict, blank=True)
    branding = models.JSONField(default=dict, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="institution_updates",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_institution_profile"
        verbose_name = "institution profile"

    def __str__(self):
        return self.institution_name


class SystemSetting(models.Model):
    """Versioned runtime configuration key-value store."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    key = models.CharField(max_length=120, unique=True, db_index=True)
    category = models.CharField(max_length=40, db_index=True)
    value = models.JSONField(default=dict)
    is_sensitive = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_setting_updates",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_setting"
        ordering = ["category", "key"]

    def __str__(self):
        return f"{self.category}.{self.key} (v{self.version})"


class SettingRevision(models.Model):
    """Immutable revision history for rollback support."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    setting = models.ForeignKey(SystemSetting, on_delete=models.CASCADE, related_name="revisions")
    setting_key = models.CharField(max_length=120, db_index=True)
    category = models.CharField(max_length=40)
    old_value = models.JSONField(default=dict)
    new_value = models.JSONField(default=dict)
    version = models.PositiveIntegerField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="setting_revisions",
    )
    change_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_setting_revision"
        ordering = ["-created_at"]


class FeatureFlag(models.Model):
    """Module toggles without code deployment."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    key = models.SlugField(max_length=80, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    last_changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_flag_changes",
    )
    last_changed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_feature_flag"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({'on' if self.enabled else 'off'})"


class MaintenanceState(models.Model):
    """Platform maintenance and emergency controls."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_enabled = models.BooleanField(default=False)
    read_only_mode = models.BooleanField(default=False)
    emergency_stop_voting = models.BooleanField(default=False)
    emergency_stop_results = models.BooleanField(default=False)
    disable_login = models.BooleanField(default=False)
    message = models.TextField(blank=True, default="VoteBridge is undergoing scheduled maintenance.")
    expected_return_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_updates",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_maintenance_state"

    def __str__(self):
        return "Maintenance ON" if self.is_enabled else "Maintenance OFF"


class BackupRecord(models.Model):
    """Backup job metadata and verification status."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        VERIFIED = "verified", "Verified"

    class BackupType(models.TextChoices):
        MANUAL = "manual", "Manual"
        SCHEDULED = "scheduled", "Scheduled"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    backup_type = models.CharField(max_length=20, choices=BackupType.choices, default=BackupType.MANUAL)
    schedule_cron = models.CharField(max_length=80, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backups_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_backup_record"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.status})"
