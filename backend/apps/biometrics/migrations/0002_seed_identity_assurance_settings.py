from django.db import migrations


def seed_identity_assurance(apps, schema_editor):
    from apps.system.services.system_service import system_settings_service

    system_settings_service.ensure_defaults()


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("biometrics", "0001_initial"),
        ("system", "0002_seed_system_defaults"),
    ]

    operations = [
        migrations.RunPython(seed_identity_assurance, unseed),
    ]
