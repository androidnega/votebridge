from django.db import migrations


def seed_settings(apps, schema_editor):
    from apps.system.services.system_service import system_settings_service

    system_settings_service.ensure_defaults()


class Migration(migrations.Migration):
    dependencies = [
        ("trusted_devices", "0001_initial"),
        ("system", "0002_seed_system_defaults"),
    ]

    operations = [
        migrations.RunPython(seed_settings, migrations.RunPython.noop),
    ]
