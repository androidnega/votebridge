from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ussd", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ussdrequestlog",
            name="http_status",
            field=models.PositiveSmallIntegerField(default=200),
        ),
        migrations.AddField(
            model_name="ussdrequestlog",
            name="provider_user_id",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="ussdrequestlog",
            name="request_payload",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="ussdrequestlog",
            name="response_payload",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
