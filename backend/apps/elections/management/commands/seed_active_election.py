"""
Seed a complete OPEN demo election for demonstrations and testing.

Run: python manage.py seed_active_election

DEV ONLY — only affects elections tagged demo_seed=True or created_by_system=True.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.candidates.services import candidate_service
from apps.dashboard.services.dashboard_service import dashboard_service
from apps.elections.models import Election, Position, VoterEligibility, VotingChannel
from apps.elections.services import (
    election_service,
    eligibility_service,
    position_service,
)
from apps.notifications.models import DeliveryLog
from apps.notifications.repositories.notification_repository import InAppNotificationRepository
from apps.notifications.services.communication_service import communication_service
from apps.results.models import ElectionResult
from apps.system.models import FeatureFlag
from apps.system.services.feature_flag_service import feature_flag_service
from apps.system.services.system_service import system_settings_service
from apps.voting.models import Vote
from core.exceptions import ValidationError

ELECTION_TITLE = "SRC General Elections 2026"
INSTITUTION = "Takoradi Technical University"

POSITIONS = [
    "President",
    "General Secretary",
    "Financial Secretary",
    "Women's Commissioner",
    "Sports Secretary",
    "Entertainment Secretary",
    "Organising Secretary",
]

# (full_name, index_number, faculty, department)
CANDIDATE_ROSTER: dict[str, list[tuple[str, str, str, str]]] = {
    "President": [
        ("Kofi Boateng", "BC/ITN/24/112", "Faculty of Applied Sciences", "Information Technology"),
        ("Ama Serwaa", "BC/ITS/24/051", "Faculty of Applied Sciences", "Computer Science"),
        ("Kwame Ansah", "BC/ITD/24/044", "Faculty of Applied Sciences", "Information Technology"),
    ],
    "General Secretary": [
        ("Efua Adjei", "BC/ACC/24/092", "Faculty of Business Studies", "Accounting"),
        ("Daniel Owusu", "BC/ITS/24/043", "Faculty of Applied Sciences", "Computer Science"),
        ("Selina Agyeman", "BC/ACC/24/095", "Faculty of Business Studies", "Accounting"),
    ],
    "Financial Secretary": [
        ("Adwoa Mensah", "BC/ACC/24/088", "Faculty of Business Studies", "Accounting"),
        ("Isaac Tetteh", "BC/MEE/24/029", "Faculty of Engineering", "Mechanical Engineering"),
        ("Rebecca Antwi", "BC/ITD/24/036", "Faculty of Applied Sciences", "Information Technology"),
    ],
    "Women's Commissioner": [
        ("Akosua Frimpong", "BC/ITD/24/048", "Faculty of Applied Sciences", "Information Technology"),
        ("Gifty Asare", "BC/ITD/24/039", "Faculty of Applied Sciences", "Information Technology"),
        ("Naana Dankwa", "BC/ICT/24/070", "Faculty of Applied Sciences", "Computer Technology"),
    ],
    "Sports Secretary": [
        ("Prince Boakye", "BC/ITN/24/105", "Faculty of Applied Sciences", "Information Technology"),
        ("Samuel Osei", "BC/ITS/24/055", "Faculty of Applied Sciences", "Computer Science"),
        ("Michael Addo", "BC/ITN/24/121", "Faculty of Applied Sciences", "Information Technology"),
    ],
    "Entertainment Secretary": [
        ("Abena Boateng", "BC/ICT/24/056", "Faculty of Applied Sciences", "Computer Technology"),
        ("Kojo Sarpong", "BC/ITN/24/118", "Faculty of Applied Sciences", "Information Technology"),
        ("Ama Kwarteng", "BC/ICT/24/061", "Faculty of Applied Sciences", "Computer Technology"),
    ],
    "Organising Secretary": [
        ("Kwesi Appiah", "BC/ITS/24/052", "Faculty of Applied Sciences", "Computer Science"),
        ("Yaw Darko", "BC/MEE/24/018", "Faculty of Engineering", "Mechanical Engineering"),
        ("Kofi Asante", "BC/ITN/24/099", "Faculty of Applied Sciences", "Information Technology"),
    ],
}


class Command(BaseCommand):
    help = "Seed (or refresh) a complete OPEN demo election for demonstrations and testing."

    def handle(self, *args, **options):
        if not User.objects.filter(role__name=Role.Name.ADMIN, is_active=True).exists():
            call_command("seed_demo_users")

        admin = User.objects.filter(role__name=Role.Name.ADMIN, is_active=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR("No active admin user found after seed_demo_users."))
            return

        student_count = User.objects.filter(role__name=Role.Name.STUDENT, is_active=True).count()
        if student_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    "  ! no active students found — run seed_demo_data for a fuller demo roster"
                )
            )

        self._ensure_platform_readiness()

        with transaction.atomic():
            election = self._resolve_or_create_election(admin)
            position_count = self._sync_positions(election)
            candidate_count = self._sync_candidates(election)
            eligible_count = self._sync_eligibility(election, admin)
            election = self._ensure_open(election, admin)
            self._clear_votes_and_results(election)
            self._seed_notifications(election, admin)

        self._refresh_dashboard_cache()

        self.stdout.write(self.style.SUCCESS("✓ Election created"))
        self.stdout.write(self.style.SUCCESS(f"✓ Positions created ({position_count})"))
        self.stdout.write(self.style.SUCCESS(f"✓ Candidates created ({candidate_count})"))
        self.stdout.write(self.style.SUCCESS(f"✓ Eligible students added ({eligible_count})"))
        self.stdout.write(self.style.SUCCESS("✓ Election opened"))
        self.stdout.write(self.style.SUCCESS("✓ Dashboard cache refreshed"))
        self.stdout.write("")
        self.stdout.write(f"  {ELECTION_TITLE} — {Election.Status.OPEN.upper()}")
        self.stdout.write(f"  Institution: {INSTITUTION}")
        self.stdout.write(f"  Closes: {election.end_date.strftime('%Y-%m-%d %H:%M %Z')}")

    def _ensure_platform_readiness(self) -> None:
        """Ensure voting channels, policies, and readiness prerequisites exist."""
        system_settings_service.ensure_defaults()
        feature_flag_service.ensure_defaults()
        FeatureFlag.objects.update_or_create(
            key="fraud_detection",
            defaults={
                "name": "Fraud Detection",
                "description": "Fraud monitoring for elections",
                "enabled": True,
            },
        )
        for channel_name in (VotingChannel.ChannelName.WEB, VotingChannel.ChannelName.USSD):
            VotingChannel.objects.get_or_create(
                channel_name=channel_name,
                defaults={"is_active": True},
            )

    def _resolve_or_create_election(self, admin: User) -> Election:
        """Return a refreshable demo election or create a new one."""
        existing = Election.objects.filter(title=ELECTION_TITLE, demo_seed=True).first()
        if existing and existing.status == Election.Status.ARCHIVED:
            existing = None

        if existing and existing.status == Election.Status.CLOSED:
            election_service.archive_election(existing.uuid)
            existing = None

        now = timezone.now()
        election_data = {
            "title": ELECTION_TITLE,
            "description": (
                f"{INSTITUTION} Student Representative Council general elections. "
                "Secure voting with SVT and OTP verification."
            ),
            "election_type": Election.ElectionType.STUDENT_UNION,
            "start_date": now,
            "end_date": now + timedelta(days=1),
            "allow_web_voting": True,
            "allow_ussd_voting": True,
            "allow_sms_notifications": False,
            "demo_seed": True,
            "created_by_system": True,
        }

        if existing:
            election = election_service.update_election(existing.uuid, election_data)
            self._archive_other_demo_elections(exclude_uuid=existing.uuid)
            return election

        self._archive_other_demo_elections()
        return election_service.create_election(admin, election_data)

    def _archive_other_demo_elections(self, *, exclude_uuid=None) -> None:
        """Safely retire prior demo-seed elections without touching production data."""
        queryset = Election.objects.filter(demo_seed=True)
        if exclude_uuid:
            queryset = queryset.exclude(uuid=exclude_uuid)

        for election in queryset:
            if election.status == Election.Status.ARCHIVED:
                continue
            if election.status == Election.Status.DRAFT:
                election_service.delete_election(election.uuid)
                continue
            if election.status == Election.Status.SCHEDULED:
                election_service.delete_election(election.uuid)
                continue
            if election.status == Election.Status.OPEN:
                election_service.pause_election(election.uuid)
            if election.status == Election.Status.PAUSED:
                election_service.close_election(election.uuid)
            election.refresh_from_db()
            if election.status == Election.Status.CLOSED:
                election_service.archive_election(election.uuid)

    def _sync_positions(self, election: Election) -> int:
        created = 0
        for order, title in enumerate(POSITIONS):
            existing = Position.objects.filter(election=election, title=title).first()
            if existing:
                position_service.update_position(
                    existing.uuid,
                    {
                        "description": f"Candidates for {title} — {INSTITUTION} SRC.",
                        "display_order": order,
                        "is_active": True,
                        "is_votable": True,
                    },
                )
            else:
                position_service.create_position(
                    election.uuid,
                    {
                        "title": title,
                        "description": f"Candidates for {title} — {INSTITUTION} SRC.",
                        "display_order": order,
                        "is_active": True,
                        "is_votable": True,
                    },
                )
                created += 1

        Position.objects.filter(election=election, title__iexact="Vice President").update(
            is_votable=False,
            is_active=False,
        )
        return Position.objects.filter(election=election, is_active=True, is_votable=True).count()

    def _sync_candidates(self, election: Election) -> int:
        total = 0
        for position_title, roster in CANDIDATE_ROSTER.items():
            position = Position.objects.filter(election=election, title=position_title).first()
            if not position:
                continue

            for i, (name, index_number, faculty, department) in enumerate(roster):
                academic_level = ("Level 200", "Level 300", "Level 400")[i % 3]
                manifesto = (
                    f"Index: {index_number}\n"
                    f"Faculty: {faculty}\n"
                    f"Department: {department}\n"
                    f"Academic Level: {academic_level}\n\n"
                    "I am committed to transparent SRC governance, accountable leadership, "
                    "and improving student welfare across campus."
                )
                existing = Candidate.objects.filter(election=election, full_name=name).first()
                if existing:
                    candidate_service.update_candidate(
                        existing.uuid,
                        {
                            "position_uuid": position.uuid,
                            "department": department,
                            "manifesto": manifesto,
                            "status": Candidate.Status.APPROVED,
                        },
                    )
                else:
                    candidate_service.create_candidate(
                        election.uuid,
                        {
                            "position_uuid": position.uuid,
                            "full_name": name,
                            "department": department,
                            "manifesto": manifesto,
                            "status": Candidate.Status.APPROVED,
                        },
                    )
                total += 1
        return total

    def _sync_eligibility(self, election: Election, admin: User) -> int:
        students = User.objects.filter(role__name=Role.Name.STUDENT, is_active=True)
        user_uuids = [str(student.uuid) for student in students]
        if not user_uuids:
            self.stdout.write(self.style.WARNING("  ! no active students — eligibility list empty"))
            return 0

        eligibility_service.bulk_set_eligibility(
            election.uuid,
            user_uuids,
            is_eligible=True,
            eligibility_reason=f"Automatically eligible — active student at {INSTITUTION}.",
            verified_by=admin,
        )
        return VoterEligibility.objects.filter(election=election, is_eligible=True).count()

    def _ensure_open(self, election: Election, admin: User) -> Election:
        election.refresh_from_db()
        if election.status == Election.Status.OPEN:
            return election

        if election.status == Election.Status.DRAFT:
            election = election_service.schedule_election(election.uuid)

        if election.status == Election.Status.SCHEDULED:
            try:
                election = election_service.open_election(election.uuid, actor=admin)
            except ValidationError as exc:
                self.stdout.write(self.style.ERROR(f"Failed to open election: {exc.message}"))
                raise

        return election

    def _clear_votes_and_results(self, election: Election) -> None:
        """Keep turnout at 0% — no ballots or results until the election closes."""
        Vote.objects.filter(election=election).delete()
        ElectionResult.objects.filter(election=election).delete()

    def _seed_notifications(self, election: Election, admin: User) -> None:
        students = list(User.objects.filter(role__name=Role.Name.STUDENT, is_active=True)[:12])
        in_app_repo = InAppNotificationRepository()

        notification_samples = [
            (
                f"{ELECTION_TITLE} is now open",
                f"Voting is open for {ELECTION_TITLE}. Cast your ballot before polls close tomorrow.",
            ),
            (
                "Voting closes tomorrow",
                f"Reminder: {ELECTION_TITLE} closes on "
                f"{election.end_date.strftime('%A %d %B at %H:%M')}. Vote now if you have not.",
            ),
        ]

        for student in students:
            context = {
                "first_name": student.first_name or "Student",
                "election_name": election.title,
                "election_uuid": str(election.uuid),
            }
            for title, body in notification_samples:
                in_app_repo.create(
                    user=student,
                    title=title,
                    body=body,
                    category="election",
                )

            if student.email:
                try:
                    communication_service.dispatch(
                        template_code="election_opening",
                        channel=DeliveryLog.Channel.IN_APP,
                        recipient=student.email,
                        context=context,
                        user=student,
                        actor=admin,
                        metadata={"source": "seed_active_election", "demo_seed": True},
                    )
                except ValidationError:
                    pass

    def _refresh_dashboard_cache(self) -> None:
        cache.delete("analytics:overview")
        cache.delete("operations:overview")

        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            payload = dashboard_service.get_admin_overview()
            realtime_broadcast_service.dashboard_stats(
                role="admin",
                user_uuid=None,
                payload=payload,
            )
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  ! dashboard broadcast skipped: {exc}"))
