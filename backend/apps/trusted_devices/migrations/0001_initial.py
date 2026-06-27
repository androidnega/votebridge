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
            name="TrustedDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("device_name", models.CharField(default="Trusted Device", max_length=128)),
                ("device_token_hash", models.CharField(db_index=True, max_length=128)),
                ("browser_fingerprint", models.CharField(db_index=True, max_length=256)),
                ("operating_system", models.CharField(blank=True, max_length=64)),
                ("browser_name", models.CharField(blank=True, max_length=64)),
                ("browser_version", models.CharField(blank=True, max_length=32)),
                ("platform", models.CharField(blank=True, max_length=64)),
                ("timezone", models.CharField(blank=True, max_length=64)),
                ("language", models.CharField(blank=True, max_length=32)),
                ("screen_resolution", models.CharField(blank=True, max_length=32)),
                ("first_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("last_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("first_country", models.CharField(blank=True, max_length=100)),
                ("last_country", models.CharField(blank=True, max_length=100)),
                ("first_city", models.CharField(blank=True, max_length=100)),
                ("last_city", models.CharField(blank=True, max_length=100)),
                ("first_seen", models.DateTimeField(auto_now_add=True)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("last_verified", models.DateTimeField(blank=True, null=True)),
                ("last_biometric", models.DateTimeField(blank=True, null=True)),
                ("risk_score", models.FloatField(default=0.0)),
                ("is_trusted", models.BooleanField(db_index=True, default=True)),
                ("is_revoked", models.BooleanField(db_index=True, default=False)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trusted_devices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "trusted device",
                "verbose_name_plural": "trusted devices",
                "db_table": "trusted_device",
                "ordering": ["-last_seen"],
            },
        ),
        migrations.CreateModel(
            name="TrustedDeviceEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("device_registered", "Device Registered"),
                            ("device_revoked", "Device Revoked"),
                            ("device_expired", "Device Expired"),
                            ("trusted_login", "Trusted Login"),
                            ("high_risk_login", "High Risk Login"),
                            ("new_country_login", "New Country Login"),
                            ("biometric_triggered", "Biometric Triggered"),
                            ("device_renamed", "Device Renamed"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("decision", models.CharField(blank=True, max_length=24)),
                ("risk_score", models.FloatField(blank=True, null=True)),
                ("browser_name", models.CharField(blank=True, max_length=64)),
                ("operating_system", models.CharField(blank=True, max_length=64)),
                ("country", models.CharField(blank=True, max_length=100)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="events",
                        to="trusted_devices.trusteddevice",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trusted_device_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "trusted_device_event",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="trusteddevice",
            index=models.Index(fields=["user", "is_trusted", "is_revoked"], name="trusted_dev_user_id_8a1b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="trusteddevice",
            index=models.Index(fields=["user", "device_token_hash"], name="trusted_dev_user_id_9d3e4f_idx"),
        ),
    ]
