"""Remove or archive elections by title (development / cleanup)."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.elections.models import Election


class Command(BaseCommand):
    help = "Archive or permanently delete an election by exact title match."

    def add_arguments(self, parser):
        parser.add_argument("title", type=str, help="Exact election title to purge")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without applying",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Permanently delete (fails when protected records exist)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        title = options["title"].strip()
        if not title:
            raise CommandError("Election title is required.")

        elections = list(Election.objects.filter(title=title))
        if not elections:
            self.stdout.write(self.style.WARNING(f"No election titled '{title}'."))
            return

        if options["dry_run"]:
            for election in elections:
                action = "delete" if options["delete"] else "archive"
                self.stdout.write(f"Would {action}: {election.title} ({election.uuid}) — {election.status}")
            return

        count = 0
        for election in elections:
            uuid = election.uuid
            title = election.title
            if options["delete"]:
                from apps.elections.services.election_purge_service import election_purge_service

                election_purge_service.purge_election(election)
                self.stdout.write(
                    self.style.SUCCESS(f"Deleted election '{title}' ({uuid}) and related records.")
                )
            else:
                election.status = Election.Status.ARCHIVED
                election.save(update_fields=["status", "updated_at"])
                self.stdout.write(self.style.SUCCESS(f"Archived election '{title}' ({uuid})."))
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Processed {count} election(s)."))
