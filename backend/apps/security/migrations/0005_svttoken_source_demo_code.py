from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0004_svttoken_ballot_session_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="svttoken",
            name="source_demo_code",
            field=models.CharField(
                blank=True,
                db_column="source_demo_code",
                db_index=True,
                default="",
                max_length=32,
            ),
        ),
    ]
