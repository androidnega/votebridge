from django.db import migrations


def seed_system_defaults(apps, schema_editor):
    from apps.system.services.system_service import (
        feature_flag_service,
        institution_service,
        system_settings_service,
    )

    system_settings_service.ensure_defaults()
    feature_flag_service.ensure_defaults()
    institution_service.get_profile()


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("system", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_system_defaults, unseed),
    ]
