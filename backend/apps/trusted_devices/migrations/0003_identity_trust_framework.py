import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trusted_devices", "0002_seed_trusted_device_settings"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="trusteddevice",
            name="device_type",
            field=models.CharField(
                choices=[("university_managed", "University Managed"), ("personal", "Personal Device")],
                db_index=True,
                default="personal",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="trusteddevice",
            name="trust_level",
            field=models.CharField(
                choices=[
                    ("HIGH", "High"),
                    ("MEDIUM", "Medium"),
                    ("LOW", "Low"),
                    ("REVOKED", "Revoked"),
                ],
                db_index=True,
                default="MEDIUM",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="trusteddevice",
            name="previous_login_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="trusteddeviceevent",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("device_registered", "Device Registered"),
                    ("device_revoked", "Device Revoked"),
                    ("device_expired", "Device Expired"),
                    ("trusted_login", "Trusted Login"),
                    ("high_risk_login", "High Risk Login"),
                    ("new_country_login", "New Country Login"),
                    ("biometric_triggered", "Biometric Triggered"),
                    ("device_renamed", "Device Renamed"),
                    ("trust_level_changed", "Trust Level Changed"),
                    ("risk_score_changed", "Risk Score Changed"),
                    ("impossible_travel", "Impossible Travel"),
                    ("device_renewed", "Device Renewed"),
                    ("session_revoked", "Session Revoked"),
                    ("university_device_assigned", "University Device Assigned"),
                ],
                db_index=True,
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="TrustedDeviceLoginHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("logged_in_at", models.DateTimeField(db_index=True)),
                ("country", models.CharField(blank=True, max_length=100)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("browser_name", models.CharField(blank=True, max_length=64)),
                ("operating_system", models.CharField(blank=True, max_length=64)),
                ("authentication_method", models.CharField(blank=True, max_length=32)),
                ("risk_score", models.FloatField(default=0.0)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="login_history",
                        to="trusted_devices.trusteddevice",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trusted_device_login_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "trusted_device_login_history",
                "ordering": ["-logged_in_at"],
                "indexes": [
                    models.Index(fields=["device", "logged_in_at"], name="td_login_dev_time_idx"),
                    models.Index(fields=["user", "logged_in_at"], name="td_login_user_time_idx"),
                ],
            },
        ),
    ]
