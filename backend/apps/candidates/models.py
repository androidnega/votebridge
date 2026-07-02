import uuid

from django.db import models


def candidate_image_path(instance, filename):
    return f"candidates/images/{instance.uuid}/{filename}"


class Candidate(models.Model):
    """Election candidate."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    election = models.ForeignKey(
        "elections.Election",
        on_delete=models.CASCADE,
        related_name="candidates",
    )
    position = models.ForeignKey(
        "elections.Position",
        on_delete=models.PROTECT,
        related_name="candidates",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="candidacies",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=255)
    department = models.CharField(max_length=150, blank=True)
    manifesto = models.TextField(blank=True)
    image = models.ImageField(upload_to=candidate_image_path, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "candidates_candidate"
        ordering = ["full_name"]
        verbose_name = "candidate"
        verbose_name_plural = "candidates"
        constraints = [
            models.UniqueConstraint(
                fields=["election", "full_name"],
                name="candidates_unique_name_per_election",
            ),
            models.UniqueConstraint(
                fields=["election", "user"],
                condition=models.Q(user__isnull=False),
                name="candidates_unique_user_per_election",
            ),
        ]
        indexes = [
            models.Index(fields=["election", "status"]),
            models.Index(fields=["position", "status"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.position.title})"
