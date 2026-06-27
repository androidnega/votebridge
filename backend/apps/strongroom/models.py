import hashlib
import json
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class BallotSeal(models.Model):
    """Immutable reference seal for a submitted ballot — no vote data duplication."""

    class Status(models.TextChoices):
        SEALED = "sealed", "Sealed"
        VERIFIED = "verified", "Verified"
        COMPROMISED = "compromised", "Compromised"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="ballot_seals",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ballot_seals",
    )
    svt_id = models.UUIDField(db_index=True)
    vote_references = models.JSONField(
        default=list,
        help_text="Ordered list of vote_id UUIDs referencing voting_vote records.",
    )
    seal_hash = models.CharField(max_length=128, db_index=True)
    vote_count = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SEALED,
        db_index=True,
    )
    sealed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "strongroom_ballot_seal"
        ordering = ["-sealed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["election", "user", "svt_id"],
                name="strongroom_unique_ballot_seal_per_svt",
            ),
        ]

    def __str__(self):
        return f"BallotSeal {self.uuid} ({self.vote_count} votes)"

    @staticmethod
    def compute_seal_hash(election_uuid, svt_id, vote_refs: list[str], vote_hashes: list[str]) -> str:
        payload = json.dumps(
            {
                "election_uuid": str(election_uuid),
                "svt_id": str(svt_id),
                "vote_references": sorted(vote_refs),
                "vote_hashes": sorted(vote_hashes),
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ElectionSeal(models.Model):
    """Cryptographic seal for a certified election."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SEALED = "sealed", "Sealed"
        LOCKED = "locked", "Locked"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.OneToOneField(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="election_seal",
    )
    election_result = models.OneToOneField(
        "results.ElectionResult",
        on_delete=models.PROTECT,
        related_name="election_seal",
        null=True,
        blank=True,
    )
    election_seal_hash = models.CharField(max_length=128, blank=True, db_index=True)
    verification_hash = models.CharField(max_length=128, blank=True, db_index=True)
    ballot_seals_digest = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    sealed_at = models.DateTimeField(null=True, blank=True)
    sealed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="election_seals_created",
    )
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="election_seals_locked",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "strongroom_election_seal"

    def __str__(self):
        return f"ElectionSeal {self.election.title} ({self.status})"

    @staticmethod
    def compute_election_seal_hash(
        election_uuid,
        result_hash: str,
        ballot_seals_digest: str,
        certified_at_iso: str,
    ) -> str:
        payload = json.dumps(
            {
                "election_uuid": str(election_uuid),
                "result_hash": result_hash,
                "ballot_seals_digest": ballot_seals_digest,
                "certified_at": certified_at_iso,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_verification_hash(election_uuid, election_seal_hash: str) -> str:
        payload = f"{election_uuid}:{election_seal_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CustodyRecord(models.Model):
    """Chain-of-custody entry for election integrity actions."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="custody_records",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custody_actions",
    )
    action = models.CharField(max_length=60, db_index=True)
    entity_type = models.CharField(max_length=40, blank=True)
    entity_uuid = models.UUIDField(null=True, blank=True)
    previous_state = models.JSONField(default=dict, blank=True)
    current_state = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "strongroom_custody_record"
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.action} @ {self.timestamp}"


class IntegrityVerification(models.Model):
    """Recorded integrity verification run."""

    class VerificationType(models.TextChoices):
        FULL = "full", "Full"
        PUBLIC = "public", "Public"
        STRONGROOM = "strongroom", "Strongroom"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="integrity_verifications",
    )
    verification_type = models.CharField(max_length=20, choices=VerificationType.choices)
    is_valid = models.BooleanField(default=False)
    integrity_score = models.PositiveSmallIntegerField(default=0)
    report = models.JSONField(default=dict, blank=True)
    verification_hash_used = models.CharField(max_length=128, blank=True)
    verified_at = models.DateTimeField(default=timezone.now)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="integrity_verifications",
    )

    class Meta:
        db_table = "strongroom_integrity_verification"
        ordering = ["-verified_at"]

    def __str__(self):
        return f"Verification {self.uuid} ({self.integrity_score}%)"
