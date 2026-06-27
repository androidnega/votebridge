import hashlib
import json
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ElectionResult(models.Model):
    """Certified election results snapshot and publication lifecycle."""

    class Status(models.TextChoices):
        PENDING_GENERATION = "pending_generation", "Pending Generation"
        GENERATED = "generated", "Generated"
        PENDING_CERTIFICATION = "pending_certification", "Pending Certification"
        CERTIFIED = "certified", "Certified"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    STATUS_TRANSITIONS = {
        Status.PENDING_GENERATION: {Status.GENERATED},
        Status.GENERATED: {Status.PENDING_CERTIFICATION, Status.GENERATED},
        Status.PENDING_CERTIFICATION: {Status.CERTIFIED, Status.GENERATED},
        Status.CERTIFIED: {Status.PUBLISHED},
        Status.PUBLISHED: {Status.ARCHIVED},
        Status.ARCHIVED: set(),
    }

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.OneToOneField(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="result",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_GENERATION,
        db_index=True,
    )
    standings = models.JSONField(default=dict, blank=True)
    integrity_report = models.JSONField(default=dict, blank=True)
    turnout_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_votes_cast = models.PositiveIntegerField(default=0)
    eligible_voters = models.PositiveIntegerField(default=0)
    result_hash = models.CharField(max_length=128, blank=True)

    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_generated",
    )
    certified_at = models.DateTimeField(null=True, blank=True)
    certified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_certified",
    )
    certification_notes = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_published",
    )
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_archived",
    )
    fraud_acknowledged = models.BooleanField(default=False)
    fraud_acknowledgment_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "results_election_result"
        ordering = ["-updated_at"]
        verbose_name = "election result"
        verbose_name_plural = "election results"

    def __str__(self):
        return f"Results for {self.election.title} ({self.status})"

    @staticmethod
    def compute_result_hash(standings: dict) -> str:
        payload = json.dumps(standings, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
