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


class StrongroomCommittee(models.Model):
    """Pre-election strong room committee configuration."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending approval"
        APPROVED = "approved", "Approved"
        LOCKED = "locked", "Locked"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.OneToOneField(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="strongroom_committee",
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    session_duration_hours = models.PositiveSmallIntegerField(default=2)
    access_policy = models.CharField(max_length=40, default="multi_custodian")
    nominated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="strongroom_committees_nominated",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="strongroom_committees_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "strongroom_committee"

    def __str__(self):
        return f"Committee {self.election.title} ({self.status})"

    @property
    def is_mutable(self) -> bool:
        return self.status in {self.Status.DRAFT, self.Status.PENDING_APPROVAL}


class StrongroomCommitteeMember(models.Model):
    """Custodian assigned to a strong room committee."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    committee = models.ForeignKey(
        StrongroomCommittee,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="strongroom_committee_memberships",
    )
    custodian_order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "strongroom_committee_member"
        ordering = ["custodian_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["committee", "user"],
                name="strongroom_unique_committee_member",
            ),
            models.UniqueConstraint(
                fields=["committee", "custodian_order"],
                name="strongroom_unique_custodian_order",
            ),
        ]

    def __str__(self):
        return f"Custodian {self.custodian_order} — {self.user}"


class VaultAccessRequest(models.Model):
    """Formal request to open the electoral strong room vault."""

    class Reason(models.TextChoices):
        COURT_ORDER = "court_order", "Court Order"
        CANDIDATE_APPEAL = "candidate_appeal", "Candidate Appeal"
        ELECTORAL_COMMISSION_REVIEW = "electoral_commission_review", "Electoral Commission Review"
        INTERNAL_AUDIT = "internal_audit", "Internal Audit"
        INTEGRITY_VERIFICATION = "integrity_verification", "Integrity Verification"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        CONSUMED = "consumed", "Consumed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="vault_access_requests",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vault_access_requests",
    )
    reason = models.CharField(max_length=40, choices=Reason.choices, db_index=True)
    justification = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vault_access_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "strongroom_vault_access_request"
        ordering = ["-created_at"]

    def __str__(self):
        return f"VaultAccess {self.election.title} ({self.reason})"


class VaultSession(models.Model):
    """Time-bound strong room vault session after multi-custodian authentication."""

    class Status(models.TextChoices):
        AWAITING_CUSTODIANS = "awaiting_custodians", "Awaiting custodians"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CLOSED = "closed", "Closed"
        RESEALED = "resealed", "Resealed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="vault_sessions",
    )
    access_request = models.OneToOneField(
        VaultAccessRequest,
        on_delete=models.PROTECT,
        related_name="vault_session",
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.AWAITING_CUSTODIANS,
        db_index=True,
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vault_sessions_initiated",
    )
    authenticated_custodians = models.JSONField(default=list, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    session_duration_hours = models.PositiveSmallIntegerField(default=2)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "strongroom_vault_session"
        ordering = ["-created_at"]

    def __str__(self):
        return f"VaultSession {self.uuid} ({self.status})"
