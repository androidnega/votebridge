import django.db.models.deletion
from django.db import migrations, models


def migrate_position_text_to_fk(apps, schema_editor):
    Candidate = apps.get_model("candidates", "Candidate")
    Position = apps.get_model("elections", "Position")

    for candidate in Candidate.objects.all():
        title = candidate.position_title
        if not title:
            continue
        position, _ = Position.objects.get_or_create(
            election_id=candidate.election_id,
            title=title,
            defaults={
                "description": "",
                "max_votes_allowed": 1,
                "display_order": 0,
                "is_active": True,
            },
        )
        candidate.position_id = position.id
        candidate.save(update_fields=["position_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("candidates", "0001_initial"),
        ("elections", "0003_position_votereligibility"),
    ]

    operations = [
        migrations.RenameField(
            model_name="candidate",
            old_name="position",
            new_name="position_title",
        ),
        migrations.AddField(
            model_name="candidate",
            name="position",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="candidates",
                to="elections.position",
            ),
        ),
        migrations.RunPython(migrate_position_text_to_fk, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="candidate",
            name="position_title",
        ),
        migrations.AlterField(
            model_name="candidate",
            name="position",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="candidates",
                to="elections.position",
            ),
        ),
        migrations.AddIndex(
            model_name="candidate",
            index=models.Index(fields=["position", "status"], name="candidates__positio_72d16c_idx"),
        ),
    ]
