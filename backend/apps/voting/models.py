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
