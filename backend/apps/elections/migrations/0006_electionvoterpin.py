import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("elections", "0005_position_is_votable"),
    ]

    operations = [
        migrations.CreateModel(
            name="ElectionVoterPin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("pin_hash", models.CharField(max_length=128)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("max_attempts", models.PositiveSmallIntegerField(default=3)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="voter_pins",
                        to="elections.election",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="election_pins",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "elections_voter_pin",
                "indexes": [
                    models.Index(fields=["election", "is_active"], name="elections_e_electio_6e8b0d_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("election", "user"),
                        name="elections_unique_pin_per_voter",
                    ),
                ],
            },
        ),
    ]
