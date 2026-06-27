from django.db import migrations


def seed_voting_channels(apps, schema_editor):
    VotingChannel = apps.get_model("elections", "VotingChannel")
    channels = [
        ("web", True),
        ("ussd", True),
        ("sms", False),
    ]
    for name, is_active in channels:
        VotingChannel.objects.get_or_create(
            channel_name=name,
            defaults={"is_active": is_active},
        )


def unseed_voting_channels(apps, schema_editor):
    VotingChannel = apps.get_model("elections", "VotingChannel")
    VotingChannel.objects.filter(channel_name__in=["web", "ussd", "sms"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("elections", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_voting_channels, unseed_voting_channels),
    ]
