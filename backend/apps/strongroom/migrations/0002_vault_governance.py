import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("elections", "0003_position_votereligibility"),
        ("strongroom", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StrongroomCommittee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("pending_approval", "Pending approval"), ("approved", "Approved"), ("locked", "Locked")], db_index=True, default="draft", max_length=24)),
                ("session_duration_hours", models.PositiveSmallIntegerField(default=2)),
                ("access_policy", models.CharField(default="multi_custodian", max_length=40)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="strongroom_committees_approved", to=settings.AUTH_USER_MODEL)),
                ("election", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="strongroom_committee", to="elections.election")),
                ("nominated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="strongroom_committees_nominated", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "strongroom_committee"},
        ),
        migrations.CreateModel(
            name="VaultAccessRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("reason", models.CharField(choices=[("court_order", "Court Order"), ("candidate_appeal", "Candidate Appeal"), ("electoral_commission_review", "Electoral Commission Review"), ("internal_audit", "Internal Audit"), ("integrity_verification", "Integrity Verification")], db_index=True, max_length=40)),
                ("justification", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied"), ("consumed", "Consumed")], db_index=True, default="pending", max_length=20)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("election", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_access_requests", to="elections.election")),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vault_access_requests", to=settings.AUTH_USER_MODEL)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vault_access_reviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "strongroom_vault_access_request", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="VaultSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("status", models.CharField(choices=[("awaiting_custodians", "Awaiting custodians"), ("active", "Active"), ("expired", "Expired"), ("closed", "Closed"), ("resealed", "Resealed")], db_index=True, default="awaiting_custodians", max_length=24)),
                ("authenticated_custodians", models.JSONField(blank=True, default=list)),
                ("opened_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("session_duration_hours", models.PositiveSmallIntegerField(default=2)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("access_request", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="vault_session", to="strongroom.vaultaccessrequest")),
                ("election", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_sessions", to="elections.election")),
                ("initiated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vault_sessions_initiated", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "strongroom_vault_session", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="StrongroomCommitteeMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("custodian_order", models.PositiveSmallIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("committee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="strongroom.strongroomcommittee")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="strongroom_committee_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "strongroom_committee_member",
                "ordering": ["custodian_order"],
            },
        ),
        migrations.AddConstraint(
            model_name="strongroomcommitteemember",
            constraint=models.UniqueConstraint(fields=("committee", "user"), name="strongroom_unique_committee_member"),
        ),
        migrations.AddConstraint(
            model_name="strongroomcommitteemember",
            constraint=models.UniqueConstraint(fields=("committee", "custodian_order"), name="strongroom_unique_custodian_order"),
        ),
    ]
