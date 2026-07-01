from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0003_alter_auditlog_event_type_alter_svttoken_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="svttoken",
            name="last_resent_at",
            field=models.DateTimeField(blank=True, db_column="last_resent_at", null=True),
        ),
        migrations.AddField(
            model_name="svttoken",
            name="validated_at",
            field=models.DateTimeField(blank=True, db_column="validated_at", null=True),
        ),
        migrations.AddField(
            model_name="svttoken",
            name="validation_attempts",
            field=models.PositiveSmallIntegerField(db_column="validation_attempts", default=0),
        ),
    ]
