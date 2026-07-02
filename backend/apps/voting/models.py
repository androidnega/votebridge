import hashlib
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Vote(models.Model):
    """Immutable ballot selection record."""

    vote_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="vote_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="votes",
        db_column="election_id",
    )
    position = models.ForeignKey(
        "elections.Position",
        on_delete=models.PROTECT,
        related_name="votes",
        db_column="position_id",
    )
    candidate = models.ForeignKey(
        "candidates.Candidate",
        on_delete=models.PROTECT,
        related_name="votes",
        db_column="candidate_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="votes",
        db_column="user_id",
    )
    channel = models.ForeignKey(
        "elections.VotingChannel",
        on_delete=models.PROTECT,
        related_name="votes",
        db_column="channel_id",
    )
    svt_id = models.UUIDField(
        null=True,
        blank=True,
        db_column="svt_id",
        help_text="Strongroom verification token — populated in Phase 5.",
    )
    vote_hash = models.CharField(max_length=128, db_column="vote_hash")
    timestamp = models.DateTimeField(default=timezone.now, db_column="timestamp")

    class Meta:
        db_table = "voting_vote"
        ordering = ["-timestamp"]
        verbose_name = "vote"
        verbose_name_plural = "votes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "position", "candidate"],
                name="voting_unique_user_position_candidate",
            ),
        ]
        indexes = [
            models.Index(fields=["election", "user"]),
            models.Index(fields=["position", "user"]),
            models.Index(fields=["vote_hash"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"Vote {self.vote_id}"

    @staticmethod
    def compute_vote_hash(
        election_id,
        position_id,
        candidate_id,
        user_id,
        channel_id,
        timestamp_iso: str,
    ) -> str:
        payload = f"{election_id}:{position_id}:{candidate_id}:{user_id}:{channel_id}:{timestamp_iso}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class PreVotePresenceCapture(models.Model):
    """Web pre-vote human presence evidence (not identity verification)."""

    class Channel(models.TextChoices):
        WEB = "web", "Web"

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column="uuid",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pre_vote_presence_captures",
        db_column="user_id",
    )
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.PROTECT,
        related_name="pre_vote_presence_captures",
        db_column="election_id",
    )
    svt_id = models.UUIDField(db_column="svt_id")
    channel = models.CharField(
        max_length=16,
        choices=Channel.choices,
        default=Channel.WEB,
        db_column="channel",
    )
    image = models.ImageField(upload_to="pre_vote_presence/%Y/%m/", db_column="image")
    captured_at = models.DateTimeField(default=timezone.now, db_column="captured_at")

    class Meta:
        db_table = "voting_pre_vote_presence_capture"
        ordering = ["-captured_at"]
        verbose_name = "pre-vote presence capture"
        verbose_name_plural = "pre-vote presence captures"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "election", "svt_id"],
                name="voting_unique_presence_per_ballot_session",
            ),
        ]
        indexes = [
            models.Index(fields=["election", "user"]),
            models.Index(fields=["svt_id"]),
            models.Index(fields=["captured_at"]),
        ]

    def __str__(self):
        return f"Presence {self.uuid} ({self.channel})"
