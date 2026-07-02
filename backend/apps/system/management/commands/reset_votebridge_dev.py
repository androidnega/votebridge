"""
Development-only full reset and bootstrap for VoteBridge.

Clears demo users, elections, votes, sessions, and activity data while preserving
platform configuration (SMS/USSD/email providers, system settings, feature flags).

Usage:
    python manage.py reset_votebridge_dev --force
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.system.services.dev_reset_service import (
    BOOTSTRAP_ELECTION_ADMIN,
    BOOTSTRAP_SUPER_ADMIN,
    DEV_RESET_CONFIRMATION,
    dev_reset_service,
)


class Command(BaseCommand):
    help = "Development reset: clear demo data and bootstrap superadmin + admin accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=f"Skip interactive confirmation (required in non-TTY environments).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "This command is blocked outside development (DEBUG must be True)."
            )

        if not options["force"]:
            self.stdout.write(self.style.WARNING("=" * 72))
            self.stdout.write(self.style.WARNING("VOTEBRIDGE DEVELOPMENT RESET"))
            self.stdout.write(self.style.WARNING("=" * 72))
            self.stdout.write(
                "This will DELETE all users, elections, votes, sessions, audit logs, "
                "and demo activity data."
            )
            self.stdout.write(
                "Platform configuration (providers, system settings, feature flags) "
                "will be PRESERVED."
            )
            self.stdout.write("")
            typed = input(f'Type "{DEV_RESET_CONFIRMATION}" to continue: ').strip()
            if typed != DEV_RESET_CONFIRMATION:
                raise CommandError("Reset cancelled — confirmation phrase did not match.")

        summary = dev_reset_service.reset_and_bootstrap()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("VoteBridge development reset complete."))
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Cleared"))
        for key, count in summary.cleared.items():
            self.stdout.write(f"  {key}: {count}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Preserved"))
        for item in summary.preserved:
            self.stdout.write(f"  {item}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Bootstrap accounts"))
        for account in summary.users_created:
            self.stdout.write(
                f"  {account['username']} ({account['role']}) — {account['email']} "
                f"phone={account['phone_number'] or '—'}"
            )

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Credentials (development only)"))
        self.stdout.write(f"  Super Admin: {BOOTSTRAP_SUPER_ADMIN['username']} / {BOOTSTRAP_SUPER_ADMIN['password']}")
        self.stdout.write(f"  Election Admin: {BOOTSTRAP_ELECTION_ADMIN['username']} / {BOOTSTRAP_ELECTION_ADMIN['password']}")
        self.stdout.write("")
        self.stdout.write("  OTP delivery: SMS to the phone on each account.")
        if summary.dev_otp_fallback_enabled:
            fallback = getattr(settings, "DEV_OTP_FALLBACK_CODE", "")
            usernames = ", ".join(getattr(settings, "DEV_OTP_FALLBACK_USERNAMES", []))
            self.stdout.write(
                self.style.WARNING(
                    f"  Dev OTP fallback enabled for [{usernames}]: use {fallback} if SMS is delayed."
                )
            )
        else:
            self.stdout.write("  Dev OTP fallback: disabled")

        self.stdout.write("")
        self.stdout.write("Login: http://localhost:5173/auth/login")
