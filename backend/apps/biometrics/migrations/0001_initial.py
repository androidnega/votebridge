import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BiometricProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("encrypted_embedding", models.TextField()),
                ("embedding_algorithm", models.CharField(default="arcface", max_length=32)),
                ("model_version", models.CharField(default="arcface_v1", max_length=32)),
                ("quality_score", models.FloatField(default=0.0)),
                ("enrollment_images_count", models.PositiveSmallIntegerField(default=0)),
                ("last_verified_at", models.DateTimeField(blank=True, null=True)),
                ("failed_attempts", models.PositiveSmallIntegerField(default=0)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="biometric_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "biometric profile",
                "verbose_name_plural": "biometric profiles",
                "db_table": "biometrics_profile",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="BiometricVerificationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("enrollment", "Enrollment"),
                            ("verification_passed", "Verification Passed"),
                            ("verification_failed", "Verification Failed"),
                            ("challenge_failed", "Challenge Failed"),
                            ("spoof_attempt", "Spoof Attempt"),
                            ("account_locked", "Account Locked"),
                            ("strongroom_verification", "Strongroom Verification"),
                            ("step_up", "Step-Up Verification"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                (
                    "outcome",
                    models.CharField(
                        choices=[("success", "Success"), ("failure", "Failure"), ("blocked", "Blocked")],
                        default="failure",
                        max_length=16,
                    ),
                ),
                ("challenge_type", models.CharField(blank=True, max_length=32)),
                ("confidence", models.FloatField(blank=True, null=True)),
                ("liveness_score", models.FloatField(blank=True, null=True)),
                ("processing_time_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("model_version", models.CharField(blank=True, max_length=32)),
                ("device_fingerprint", models.CharField(blank=True, max_length=128)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="biometric_verification_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "biometrics_verification_log",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "event_type"], name="biometrics__user_id_6a0b0d_idx"),
                    models.Index(fields=["created_at", "event_type"], name="biometrics__created_8f2c1a_idx"),
                ],
            },
        ),
    ]
