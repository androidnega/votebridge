import django.db.models.deletion
from django.db import migrations, models


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    defaults = [
        ("student", "Student voter account."),
        ("candidate", "Election candidate account."),
        ("admin", "Election administrator account."),
        ("super_admin", "Platform super administrator account."),
    ]
    for name, description in defaults:
        Role.objects.get_or_create(
            name=name,
            defaults={"description": description, "is_active": True},
        )


def assign_default_role_and_require_role(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Role = apps.get_model("accounts", "Role")
    default_role = Role.objects.filter(name="student").first()
    if default_role:
        User.objects.filter(role__isnull=True).update(role=default_role)


def unseed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(
        name__in=["student", "candidate", "admin", "super_admin"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_role_user_fields"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
        migrations.RunPython(
            assign_default_role_and_require_role,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="accounts.role",
            ),
        ),
    ]
