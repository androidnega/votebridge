# Generated manually for pre-vote presence capture

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("elections", "0003_position_votereligibility"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("voting", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PreVotePresenceCapture",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        db_column="uuid",
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("svt_id", models.UUIDField(db_column="svt_id")),
                (
                    "channel",
                    models.CharField(
                        choices=[("web", "Web")],
                        db_column="channel",
                        default="web",
                        max_length=16,
                    ),
                ),
                ("image", models.ImageField(db_column="image", upload_to="pre_vote_presence/%Y/%m/")),
                (
                    "captured_at",
                    models.DateTimeField(
                        db_column="captured_at",
                        default=django.utils.timezone.now,
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        db_column="election_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pre_vote_presence_captures",
                        to="elections.election",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pre_vote_presence_captures",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "pre-vote presence capture",
                "verbose_name_plural": "pre-vote presence captures",
                "db_table": "voting_pre_vote_presence_capture",
                "ordering": ["-captured_at"],
            },
        ),
        migrations.AddIndex(
            model_name="prevotepresencecapture",
            index=models.Index(fields=["election", "user"], name="voting_pre__electio_6a1b0d_idx"),
        ),
        migrations.AddIndex(
            model_name="prevotepresencecapture",
            index=models.Index(fields=["svt_id"], name="voting_pre__svt_id_7381ed_idx"),
        ),
        migrations.AddIndex(
            model_name="prevotepresencecapture",
            index=models.Index(fields=["captured_at"], name="voting_pre__capture_4f2c91_idx"),
        ),
        migrations.AddConstraint(
            model_name="prevotepresencecapture",
            constraint=models.UniqueConstraint(
                fields=("user", "election", "svt_id"),
                name="voting_unique_presence_per_ballot_session",
            ),
        ),
    ]
