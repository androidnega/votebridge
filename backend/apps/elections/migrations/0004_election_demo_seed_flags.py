from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("elections", "0003_position_votereligibility"),
    ]

    operations = [
        migrations.AddField(
            model_name="election",
            name="created_by_system",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="True when created by automated system seeders.",
            ),
        ),
        migrations.AddField(
            model_name="election",
            name="demo_seed",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="True for elections created by demo seed commands only.",
            ),
        ),
    ]
