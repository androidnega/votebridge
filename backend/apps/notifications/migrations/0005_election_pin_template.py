from django.db import migrations


def seed_election_pin_template(apps, schema_editor):
    NotificationTemplate = apps.get_model("notifications", "NotificationTemplate")
    NotificationTemplate.objects.update_or_create(
        code="election_pin",
        defaults={
            "name": "Election PIN (USSD)",
            "channel": "multi",
            "subject": "{election_title} — Your Election PIN",
            "body_text": (
                "VoteBridge — {institution_name}\n\n"
                "{election_title}\n\n"
                "Your Election PIN: {election_pin}\n\n"
                "Use this PIN ONLY for USSD voting. Do not share it.\n"
                "This PIN expires when the election closes."
            ),
            "sms_body": (
                "VoteBridge\n"
                "{institution_name}\n"
                "{election_title}\n"
                "Your Election PIN: {election_pin}\n"
                "Use this PIN ONLY for USSD voting.\n"
                "Do not share it.\n"
                "This PIN expires when the election closes."
            ),
            "in_app_title": "Election PIN issued",
            "in_app_body": "Your USSD Election PIN for {election_title} was sent by SMS.",
            "placeholders": ["institution_name", "election_title", "election_pin"],
            "is_active": True,
        },
    )


def unseed(apps, schema_editor):
    NotificationTemplate = apps.get_model("notifications", "NotificationTemplate")
    NotificationTemplate.objects.filter(code="election_pin").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_alter_communicationprovider_provider_type"),
    ]

    operations = [
        migrations.RunPython(seed_election_pin_template, unseed),
    ]
