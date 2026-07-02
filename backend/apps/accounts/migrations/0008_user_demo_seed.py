from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_pre_vote_presence_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="demo_seed",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Seeded demo account — enables dev OTP/SVT fallbacks in DEBUG.",
            ),
        ),
    ]
