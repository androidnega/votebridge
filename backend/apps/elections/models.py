import uuid

from django.conf import settings
from django.db import models


class Election(models.Model):
    """Campus election configuration and lifecycle."""

    class ElectionType(models.TextChoices):
        GENERAL = "general", "General"
        STUDENT_UNION = "student_union", "Student Union"
        FACULTY = "faculty", "Faculty"
        DEPARTMENTAL = "departmental", "Departmental"
        SPECIAL = "special", "Special"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        OPEN = "open", "Open"
        PAUSED = "paused", "Paused"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    VOTING_ACTIVE_STATUSES = {Status.OPEN, Status.PAUSED, Status.CLOSED, Status.ARCHIVED}
    READ_ONLY_STATUSES = {Status.CLOSED, Status.ARCHIVED}

    STATUS_TRANSITIONS = {
        Status.DRAFT: {Status.SCHEDULED},
        Status.SCHEDULED: {Status.OPEN, Status.DRAFT},
        Status.OPEN: {Status.PAUSED, Status.CLOSED},
        Status.PAUSED: {Status.OPEN, Status.CLOSED},
        Status.CLOSED: {Status.ARCHIVED},
        Status.ARCHIVED: set(),
    }

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    election_type = models.CharField(max_length=30, choices=ElectionType.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    allow_web_voting = models.BooleanField(default=True)
    allow_ussd_voting = models.BooleanField(default=False)
    allow_sms_notifications = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="elections_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "elections_election"
        ordering = ["-created_at"]
        verbose_name = "election"
        verbose_name_plural = "elections"
        indexes = [
            models.Index(fields=["status", "start_date"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_read_only(self) -> bool:
        return self.status in self.READ_ONLY_STATUSES

    @property
    def voting_has_begun(self) -> bool:
        return self.status in self.VOTING_ACTIVE_STATUSES


class VotingChannel(models.Model):
    """Registered voting channel (Web, USSD, SMS)."""

    class ChannelName(models.TextChoices):
        WEB = "web", "Web"
        USSD = "ussd", "USSD"
        SMS = "sms", "SMS"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    channel_name = models.CharField(max_length=20, choices=ChannelName.choices, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "elections_voting_channel"
        ordering = ["channel_name"]
        verbose_name = "voting channel"
        verbose_name_plural = "voting channels"

    def __str__(self):
        return self.get_channel_name_display()


class Position(models.Model):
    """Elective office or race within an election."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="positions",
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    max_votes_allowed = models.PositiveSmallIntegerField(default=1)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "elections_position"
        ordering = ["display_order", "title"]
        verbose_name = "position"
        verbose_name_plural = "positions"
        constraints = [
            models.UniqueConstraint(
                fields=["election", "title"],
                name="elections_unique_position_title_per_election",
            ),
        ]
        indexes = [
            models.Index(fields=["election", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.election.title})"

    @property
    def is_single_choice(self) -> bool:
        return self.max_votes_allowed == 1

    @property
    def is_multi_choice(self) -> bool:
        return self.max_votes_allowed > 1


class VoterEligibility(models.Model):
    """Records whether a voter is eligible to participate in an election."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="voter_eligibilities",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="election_eligibilities",
    )
    is_eligible = models.BooleanField(default=True, db_index=True)
    eligibility_reason = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eligibility_verifications",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "elections_voter_eligibility"
        ordering = ["-created_at"]
        verbose_name = "voter eligibility"
        verbose_name_plural = "voter eligibilities"
        constraints = [
            models.UniqueConstraint(
                fields=["election", "user"],
                name="elections_unique_voter_per_election",
            ),
        ]
        indexes = [
            models.Index(fields=["election", "is_eligible"]),
        ]

    def __str__(self):
        status = "eligible" if self.is_eligible else "ineligible"
        return f"{self.user.email} — {self.election.title} ({status})"
