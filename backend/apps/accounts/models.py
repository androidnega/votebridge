import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Application role used for role-based access control."""

    class Name(models.TextChoices):
        STUDENT = "student", "Student"
        CANDIDATE = "candidate", "Candidate"
        ADMIN = "admin", "Admin"
        SUPER_ADMIN = "super_admin", "Super Admin"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=50, choices=Name.choices, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_role"
        ordering = ["name"]
        verbose_name = "role"
        verbose_name_plural = "roles"

    def __str__(self):
        return self.get_name_display()


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _require_role(self, extra_fields):
        role = extra_fields.get("role")
        if role is None:
            role = Role.objects.filter(name=Role.Name.SUPER_ADMIN).first()
            if role is None:
                role = Role.objects.order_by("id").first()
            if role is None:
                raise ValueError("No roles exist. Run migrations before creating users.")
            extra_fields["role"] = role
        return extra_fields

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        extra_fields = self._require_role(extra_fields)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        super_admin_role = Role.objects.filter(name=Role.Name.SUPER_ADMIN).first()
        if super_admin_role:
            extra_fields["role"] = super_admin_role

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    VoteBridge user account.

    The ``password`` field is stored in the database column ``password_hash``.
  """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
    )
    index_number = models.CharField(max_length=50, blank=True, db_index=True)
    student_id = models.CharField(max_length=50, blank=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    password = models.CharField(max_length=128, db_column="password_hash")

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "accounts_user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["index_number"],
                condition=models.Q(index_number__gt=""),
                name="accounts_user_unique_index_number",
            ),
            models.UniqueConstraint(
                fields=["student_id"],
                condition=models.Q(student_id__gt=""),
                name="accounts_user_unique_student_id",
            ),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def password_hash(self):
        return self.password

    @password_hash.setter
    def password_hash(self, raw_password):
        self.set_password(raw_password)


class OTPRequest(models.Model):
    """One-time password request for login and MFA verification."""

    class Purpose(models.TextChoices):
        LOGIN = "login", "Login"
        MFA = "mfa", "Multi-Factor Authentication"

    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_requests")
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices)
    otp_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_otp_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "purpose", "is_verified"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"OTP {self.purpose} for {self.user.email}"


class MFALog(models.Model):
    """Login and MFA audit log."""

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILED = "login_failed", "Login Failed"
        OTP_SENT = "otp_sent", "OTP Sent"
        OTP_VERIFIED = "otp_verified", "OTP Verified"
        OTP_FAILED = "otp_failed", "OTP Failed"
        MFA_REQUIRED = "mfa_required", "MFA Required"
        MFA_COMPLETED = "mfa_completed", "MFA Completed"
        LOGOUT = "logout", "Logout"
        SESSION_REVOKED = "session_revoked", "Session Revoked"
        TOKEN_REFRESH = "token_refresh", "Token Refresh"
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
        PRE_VOTE_PRESENCE_CAPTURED = "pre_vote_presence_captured", "Pre-Vote Presence Captured"
        BIO_ENROLLMENT = "bio_enrollment", "Biometric Enrollment"
        BIO_VERIFY_PASS = "bio_verify_pass", "Biometric Verification Passed"
        BIO_VERIFY_FAIL = "bio_verify_fail", "Biometric Verification Failed"
        BIO_CHALLENGE_FAIL = "bio_challenge_fail", "Biometric Challenge Failed"
        BIO_SPOOF_ATTEMPT = "bio_spoof_attempt", "Biometric Spoof Attempt"
        BIO_ACCOUNT_LOCKED = "bio_account_locked", "Biometric Account Locked"
        BIO_STRONGROOM = "bio_strongroom", "Biometric Strongroom Verification"
        BIO_STEP_UP = "bio_step_up", "Biometric Step-Up"
        DEVICE_REGISTERED = "device_registered", "Device Registered"
        DEVICE_REVOKED = "device_revoked", "Device Revoked"
        DEVICE_EXPIRED = "device_expired", "Device Expired"
        TRUSTED_LOGIN = "trusted_login", "Trusted Login"
        HIGH_RISK_LOGIN = "high_risk_login", "High Risk Login"
        NEW_COUNTRY_LOGIN = "new_country_login", "New Country Login"
        BIOMETRIC_TRIGGERED = "biometric_triggered", "Biometric Triggered"
        TRUST_LEVEL_CHANGED = "trust_level_changed", "Trust Level Changed"
        RISK_SCORE_CHANGED = "risk_score_changed", "Risk Score Changed"
        IMPOSSIBLE_TRAVEL = "impossible_travel", "Impossible Travel"
        DEVICE_RENEWED = "device_renewed", "Device Renewed"
        UNIVERSITY_DEVICE_ASSIGNED = "university_device_assigned", "University Device Assigned"
        DEVICE_RENAMED = "device_renamed", "Device Renamed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mfa_logs",
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "accounts_mfa_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.created_at})"


class Session(models.Model):
    """Tracked JWT session bound to a refresh token."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_sessions")
    refresh_token_jti = models.CharField(max_length=64, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField()
    last_activity_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_session"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"Session {self.uuid} ({self.user.email})"
