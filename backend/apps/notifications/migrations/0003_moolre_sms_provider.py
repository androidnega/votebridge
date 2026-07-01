from django.db import migrations


def seed_moolre_provider(apps, schema_editor):
    Provider = apps.get_model("notifications", "CommunicationProvider")
    Provider.objects.get_or_create(
        provider_type="moolre_sms",
        name="Moolre SMS",
        defaults={
            "is_active": True,
            "is_default": False,
            "config": {"environment": "live"},
        },
    )


def unseed_moolre_provider(apps, schema_editor):
    Provider = apps.get_model("notifications", "CommunicationProvider")
    Provider.objects.filter(provider_type="moolre_sms").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_seed_templates"),
    ]

    operations = [
        migrations.RunPython(seed_moolre_provider, unseed_moolre_provider),
    ]
