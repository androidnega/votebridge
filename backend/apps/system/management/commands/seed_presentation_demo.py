"""
Seed VoteBridge presentation demo data (TTU SRC live + FASSA historical).

Usage:
    python manage.py seed_presentation_demo --force

DEV ONLY — clears operational data while preserving platform configuration.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.system.services.presentation_demo_service import presentation_demo_service


class Command(BaseCommand):
    help = "Reset operational data and seed TTU presentation demo (SRC + FASSA)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Skip interactive confirmation.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("This command is blocked outside development (DEBUG must be True).")

        if not options["force"]:
            self.stdout.write(self.style.WARNING("This will CLEAR users/elections/votes and reseed presentation data."))
            typed = input('Type "SEED PRESENTATION" to continue: ').strip()
            if typed != "SEED PRESENTATION":
                raise CommandError("Cancelled.")

        summary = presentation_demo_service.seed()

        self.stdout.write(self.style.SUCCESS("Presentation demo seed complete."))
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Staff accounts"))
        for account in summary.staff_accounts:
            self.stdout.write(
                f"  {account['username']} ({account['role']}) — {account['email']} "
                f"password={account['password']} OTP fallback={account['otp_fallback']}"
            )

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Students"))
        self.stdout.write(f"  {summary.student_count} TTU demo students (demo_seed=True)")
        self.stdout.write(f"  Login: index number + OTP fallback {summary.demo_otp_fallback}")
        self.stdout.write(f"  Example: BC/ITS/24/047 (Kwame Mensah)")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Active SRC election"))
        for key, value in summary.src_election.items():
            self.stdout.write(f"  {key}: {value}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Past FASSA election"))
        for key, value in summary.fassa_election.items():
            self.stdout.write(f"  {key}: {value}")

        if summary.strongroom.get("configured"):
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("Strongroom committee"))
            for custodian in summary.strongroom.get("custodians", []):
                self.stdout.write(
                    f"  {custodian['username']} — password={custodian['password']} "
                    f"OTP fallback={custodian['otp_fallback']}"
                )

        self.stdout.write("")
        self.stdout.write(f"SVT demo fallback for seeded students: {summary.demo_svt_fallback}")
        self.stdout.write("Login: http://localhost:5173/auth/login")
