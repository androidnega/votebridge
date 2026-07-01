from django.db import migrations, models


def hide_appointed_src_roles(apps, schema_editor):
    Position = apps.get_model("elections", "Position")
    appointed_titles = ["Vice President"]
    Position.objects.filter(title__in=appointed_titles).update(is_votable=False)


class Migration(migrations.Migration):

    dependencies = [
        ("elections", "0004_election_demo_seed_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="position",
            name="is_votable",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="When false, the position is excluded from student ballots (e.g. appointed roles).",
            ),
        ),
        migrations.RunPython(hide_appointed_src_roles, migrations.RunPython.noop),
    ]
