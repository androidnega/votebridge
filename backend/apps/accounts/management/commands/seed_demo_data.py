"""
Populate VoteBridge with comprehensive development demo data.

Run: python manage.py seed_demo_data

DEV ONLY — uses demo passwords documented in seed_demo_users.
"""

from datetime import timedelta
import uuid as uuid_mod

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.system.dev_credentials import require_dev_bootstrap_password
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility, VotingChannel
from apps.fraud.models import FraudCase, SecurityAlert
from apps.results.models import ElectionResult
from apps.security.models import AuditLog
from apps.strongroom.models import BallotSeal, CustodyRecord, ElectionSeal
from apps.voting.models import Vote

EXTRA_STUDENTS = [
    ("Abena", "Boateng", "BC/ICT/24/056", "abena.boateng@ttu.edu.gh"),
    ("Yaw", "Darko", "BC/MEE/24/018", "yaw.darko@ttu.edu.gh"),
    ("Efua", "Adjei", "BC/ACC/24/092", "efua.adjei@ttu.edu.gh"),
    ("Kwesi", "Appiah", "BC/ITS/24/052", "kwesi.appiah@ttu.edu.gh"),
    ("Akosua", "Frimpong", "BC/ITD/24/048", "akosua.frimpong@ttu.edu.gh"),
    ("Kojo", "Sarpong", "BC/ITN/24/118", "kojo.sarpong@ttu.edu.gh"),
    ("Ama", "Kwarteng", "BC/ICT/24/061", "ama.kwarteng@ttu.edu.gh"),
    ("Fiifi", "Amoah", "BC/MEE/24/022", "fiifi.amoah@ttu.edu.gh"),
    ("Adwoa", "Mensah", "BC/ACC/24/088", "adwoa.mensah@ttu.edu.gh"),
    ("Samuel", "Osei", "BC/ITS/24/055", "samuel.osei@ttu.edu.gh"),
    ("Gifty", "Asare", "BC/ITD/24/039", "gifty.asare@ttu.edu.gh"),
    ("Prince", "Boakye", "BC/ITN/24/105", "prince.boakye@ttu.edu.gh"),
    ("Naana", "Dankwa", "BC/ICT/24/070", "naana.dankwa@ttu.edu.gh"),
    ("Isaac", "Tetteh", "BC/MEE/24/029", "isaac.tetteh@ttu.edu.gh"),
    ("Selina", "Agyeman", "BC/ACC/24/095", "selina.agyeman@ttu.edu.gh"),
    ("Daniel", "Owusu", "BC/ITS/24/043", "daniel.owusu@ttu.edu.gh"),
    ("Rebecca", "Antwi", "BC/ITD/24/036", "rebecca.antwi@ttu.edu.gh"),
    ("Michael", "Addo", "BC/ITN/24/121", "michael.addo@ttu.edu.gh"),
]

CANDIDATE_NAMES = [
    ("Kofi Boateng", "Information Technology", "BC/ITN/24/112"),
    ("Ama Serwaa", "Computer Science", "BC/ITS/24/051"),
    ("Kwame Ansah", "Information Technology", "BC/ITD/24/044"),
    ("Abena Ofori", "Computer Technology", "BC/ICT/24/063"),
]

OPEN_ELECTION_CANDIDATES = {
    "President": CANDIDATE_NAMES,
    "General Secretary": [
        ("Efua Adjei", "Accounting", "BC/ACC/24/092"),
        ("Kwame Ansah", "Information Technology", "BC/ITD/24/044"),
    ],
}

# Hourly vote weights for the last 24h (sum must fit eligible voters × positions).
DASHBOARD_HOURLY_VOTE_WEIGHTS = [
    1, 2, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 14, 12, 10, 8, 6, 5, 4, 3, 2, 2, 1, 1,
]


class Command(BaseCommand):
    help = "Seed comprehensive demo data for all VoteBridge modules (development only)."

    def handle(self, *args, **options):
        call_command("seed_demo_users")
        demo_password = require_dev_bootstrap_password()

        student_role = Role.objects.get(name=Role.Name.STUDENT)
        for first, last, index, email in EXTRA_STUDENTS:
            user, created = User.objects.update_or_create(
                email=email,
                defaults={
                    "role": student_role,
                    "first_name": first,
                    "last_name": last,
                    "index_number": index,
                    "student_id": index,
                    "is_verified": True,
                    "is_active": True,
                },
            )
            user.set_password(demo_password)
            user.save()
            if created:
                self.stdout.write(f"  + student {index}")

        admin = User.objects.filter(role__name=Role.Name.ADMIN).first()
        if not admin:
            self.stdout.write(self.style.ERROR("Admin user missing after seed_demo_users."))
            return

        now = timezone.now()
        elections_spec = [
            {
                "title": "SRC General Elections 2025",
                "description": "Archived demo election — superseded by current season.",
                "election_type": Election.ElectionType.STUDENT_UNION,
                "status": Election.Status.ARCHIVED,
                "start": now - timedelta(days=90),
                "end": now - timedelta(days=83),
                "positions": ["President", "General Secretary"],
            },
            {
                "title": "Faculty of Applied Sciences Rep Election",
                "description": "Faculty representative election — paused for audit review.",
                "election_type": Election.ElectionType.FACULTY,
                "status": Election.Status.PAUSED,
                "start": now - timedelta(days=10),
                "end": now + timedelta(days=14),
                "positions": ["Faculty Representative"],
            },
            {
                "title": "Departmental IT Officer Election 2024",
                "description": "Closed departmental election — archived for demo.",
                "election_type": Election.ElectionType.DEPARTMENTAL,
                "status": Election.Status.CLOSED,
                "start": now - timedelta(days=60),
                "end": now - timedelta(days=53),
                "positions": ["Departmental Officer"],
            },
            {
                "title": "Special Referendum — Campus Wi-Fi Policy",
                "description": "Draft referendum on updated campus connectivity policy.",
                "election_type": Election.ElectionType.SPECIAL,
                "status": Election.Status.DRAFT,
                "start": now + timedelta(days=30),
                "end": now + timedelta(days=37),
                "positions": ["Referendum"],
            },
        ]

        elections = []
        for spec in elections_spec:
            election, _ = Election.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "description": spec["description"],
                    "election_type": spec["election_type"],
                    "status": spec["status"],
                    "start_date": spec["start"],
                    "end_date": spec["end"],
                    "allow_web_voting": True,
                    "allow_ussd_voting": spec["status"] == Election.Status.OPEN,
                    "created_by": admin,
                },
            )
            elections.append(election)

            for order, pos_title in enumerate(spec["positions"]):
                Position.objects.update_or_create(
                    election=election,
                    title=pos_title,
                    defaults={
                        "description": f"Candidates for {pos_title}.",
                        "display_order": order,
                        "is_active": True,
                    },
                )

        open_election = elections[0]
        self._seed_open_election_candidates(open_election)
        self._seed_dashboard_activity(open_election, admin, now)

        student = User.objects.filter(index_number="BC/ITS/24/047").first()
        alert_samples = [
            (
                SecurityAlert.AlertType.EXCESSIVE_LOGIN_ATTEMPTS,
                SecurityAlert.Status.OPEN,
                "Repeated failed login attempts detected",
            ),
            (
                SecurityAlert.AlertType.SUSPICIOUS_VOTING_PATTERN,
                SecurityAlert.Status.REVIEWING,
                "Unusual voting velocity from single device",
            ),
            (
                SecurityAlert.AlertType.DUPLICATE_DEVICE,
                SecurityAlert.Status.RESOLVED,
                "Multiple accounts accessed from same device fingerprint",
            ),
        ]

        for alert_type, status, title in alert_samples:
            alert, created = SecurityAlert.objects.get_or_create(
                title=title,
                alert_type=alert_type,
                defaults={
                    "status": status,
                    "user": student,
                    "election": open_election,
                    "description": f"Demo security alert: {title}",
                    "metadata": {"demo": True, "source": "seed_demo_data"},
                },
            )
            if created and status != SecurityAlert.Status.RESOLVED:
                FraudCase.objects.get_or_create(
                    related_alert=alert,
                    defaults={
                        "election": open_election,
                        "user": student,
                        "severity": FraudCase.Severity.MEDIUM,
                        "status": FraudCase.Status.INVESTIGATING,
                        "risk_score": 62,
                        "investigation_notes": "Demo fraud case for dashboard review.",
                    },
                )

        closed_election = elections[2]
        closed_result, _ = ElectionResult.objects.update_or_create(
            election=closed_election,
            defaults={
                "status": ElectionResult.Status.CERTIFIED,
                "standings": {
                    "Departmental Officer": [
                        {"candidate": "Kwame Mensah", "votes": 412, "percentage": 54.2},
                        {"candidate": "Ama Osei", "votes": 349, "percentage": 45.8},
                    ]
                },
                "turnout_percentage": 68.5,
                "total_votes_cast": 761,
                "eligible_voters": 1110,
                "generated_at": now - timedelta(days=52),
                "certified_at": now - timedelta(days=51),
                "generated_by": admin,
                "certified_by": admin,
            },
        )

        ElectionSeal.objects.update_or_create(
            election=closed_election,
            defaults={
                "election_result": closed_result,
                "election_seal_hash": closed_election.uuid.hex[:64],
                "verification_hash": closed_result.uuid.hex[:64],
                "ballot_seals_digest": "demo-ballot-digest",
                "sealed_by": admin,
                "sealed_at": now - timedelta(days=51),
                "status": ElectionSeal.Status.SEALED,
            },
        )

        closed_result.status = ElectionResult.Status.PUBLISHED
        closed_result.published_at = now - timedelta(days=50)
        closed_result.published_by = admin
        closed_result.save(update_fields=["status", "published_at", "published_by"])

        self._seed_demo_votes(closed_election, admin, now)
        self._seed_audit_logs(open_election, closed_election, student, admin, now)
        self._seed_strongroom_custody(closed_election, admin, now)
        self._seed_biometric_profiles()

        call_command("seed_communication_demo")
        call_command("seed_ussd_demo")

        self.stdout.write(self.style.SUCCESS("Comprehensive demo data seeded successfully."))
        self.stdout.write(
            self.style.SUCCESS(
                "Dashboard trends: open election has hourly votes, turnout, and USSD activity."
            )
        )
        self.stdout.write("")
        self.stdout.write("Run: python manage.py seed_demo_users  (users only)")
        self.stdout.write("Run: python manage.py seed_demo_data  (full platform demo)")

    def _seed_open_election_candidates(self, open_election):
        """Approved candidates for every position on the live open election."""
        for pos_title, roster in OPEN_ELECTION_CANDIDATES.items():
            position = Position.objects.filter(election=open_election, title=pos_title).first()
            if not position:
                continue
            for name, dept, _index in roster:
                Candidate.objects.update_or_create(
                    election=open_election,
                    full_name=name,
                    defaults={
                        "position": position,
                        "department": dept,
                        "manifesto": "Committed to transparent governance and student welfare.",
                        "status": Candidate.Status.APPROVED,
                    },
                )

    def _seed_dashboard_activity(self, open_election, admin, now):
        """Eligibility, votes across the last 24h, and USSD sessions for admin charts."""
        student_role = Role.objects.get(name=Role.Name.STUDENT)
        students = list(
            User.objects.filter(role=student_role, is_active=True).order_by("index_number")
        )
        if not students:
            self.stdout.write(self.style.WARNING("  ! no students — skipping dashboard vote seed"))
            return

        for student in students:
            VoterEligibility.objects.update_or_create(
                election=open_election,
                user=student,
                defaults={
                    "is_eligible": True,
                    "eligibility_reason": "Demo eligibility for dashboard metrics.",
                    "verified_by": admin,
                    "verified_at": now,
                },
            )

        web_channel = VotingChannel.objects.filter(channel_name=VotingChannel.ChannelName.WEB).first()
        ussd_channel = VotingChannel.objects.filter(channel_name=VotingChannel.ChannelName.USSD).first()
        if not web_channel or not ussd_channel:
            self.stdout.write(self.style.WARNING("  ! voting channels missing — run migrations"))
            return

        positions = list(
            Position.objects.filter(election=open_election, is_active=True).order_by("display_order")
        )
        if not positions:
            return

        Vote.objects.filter(election=open_election).delete()

        voted_pairs: set[tuple[int, int]] = set()
        vote_total = 0
        election_uuid = str(open_election.uuid)

        for hour_idx, weight in enumerate(DASHBOARD_HOURLY_VOTE_WEIGHTS):
            bucket_start = (now - timedelta(hours=23 - hour_idx)).replace(minute=0, second=0, microsecond=0)
            for slot in range(weight):
                student = students[vote_total % len(students)]
                position = positions[vote_total % len(positions)]
                pair = (student.pk, position.pk)
                if pair in voted_pairs:
                    found = False
                    for alt_student in students:
                        alt_pair = (alt_student.pk, position.pk)
                        if alt_pair not in voted_pairs:
                            student = alt_student
                            pair = alt_pair
                            found = True
                            break
                    if not found:
                        vote_total += 1
                        continue

                candidates = list(
                    Candidate.objects.filter(
                        election=open_election,
                        position=position,
                        status=Candidate.Status.APPROVED,
                    )
                )
                if not candidates:
                    vote_total += 1
                    continue

                candidate = candidates[vote_total % len(candidates)]
                channel = ussd_channel if vote_total % 4 == 0 else web_channel
                timestamp = bucket_start + timedelta(minutes=4 + (slot * 4) % 52, seconds=vote_total % 59)
                ts_iso = timestamp.isoformat()
                vote_hash = Vote.compute_vote_hash(
                    open_election.pk,
                    position.pk,
                    candidate.pk,
                    student.pk,
                    channel.pk,
                    ts_iso,
                )
                Vote.objects.create(
                    election=open_election,
                    position=position,
                    candidate=candidate,
                    user=student,
                    channel=channel,
                    vote_hash=vote_hash,
                    timestamp=timestamp,
                )
                voted_pairs.add(pair)
                vote_total += 1

        self._seed_dashboard_ussd_sessions(open_election, students, now)
        self.stdout.write(
            f"  + dashboard activity: {vote_total} votes, "
            f"{len(students)} eligible voters on {open_election.title!r}"
        )

    def _seed_dashboard_ussd_sessions(self, open_election, students, now):
        """USSD sessions linked to the open election for live monitoring widgets."""
        from apps.ussd.models import USSDRequestLog, USSDSession

        election_uuid = str(open_election.uuid)
        samples = [
            ("sess-live-001", "233241234567", USSDSession.Status.COMPLETED, True, "VOTE_CONFIRM"),
            ("sess-live-002", "233209876543", USSDSession.Status.FAILED, False, "AUTH_PIN"),
            ("sess-live-003", "233551112233", USSDSession.Status.ACTIVE, False, "VOTE_POSITION"),
            ("sess-live-004", "233244455566", USSDSession.Status.COMPLETED, True, "MAIN_MENU"),
            ("sess-live-005", "233277788899", USSDSession.Status.FAILED, False, "VOTE_CONFIRM"),
            ("sess-live-006", "233200011122", USSDSession.Status.ACTIVE, False, "AUTH_PIN"),
        ]

        for i, (sid, msisdn, status, voted, step) in enumerate(samples):
            student = students[i % len(students)] if students else None
            session, _ = USSDSession.objects.update_or_create(
                session_id=sid,
                defaults={
                    "msisdn": msisdn,
                    "user": student,
                    "status": status,
                    "current_step": step,
                    "completed_vote": voted,
                    "request_count": 4 + i,
                    "started_at": now - timedelta(hours=2 + i),
                    "last_activity_at": now - timedelta(minutes=15 * i),
                    "ended_at": now - timedelta(minutes=5) if status != USSDSession.Status.ACTIVE else None,
                    "state_data": {
                        "demo": True,
                        "source": "seed_demo_data",
                        "election_uuid": election_uuid,
                        "user_uuid": str(student.uuid) if student else None,
                    },
                },
            )
            USSDRequestLog.objects.get_or_create(
                session=session,
                carrier_session_id=sid,
                msisdn=msisdn,
                step_after=step,
                defaults={
                    "raw_input": "1*1",
                    "parsed_inputs": ["1", "1"],
                    "outcome": (
                        USSDRequestLog.Outcome.SUCCESS
                        if status == USSDSession.Status.COMPLETED
                        else USSDRequestLog.Outcome.ERROR
                    ),
                    "response_message": "CON Demo USSD response",
                    "duration_ms": 140 + i * 12,
                },
            )

    def _seed_demo_votes(self, closed_election, admin, now):
        """Seed votes for closed election demo results."""
        web_channel = VotingChannel.objects.filter(channel_name="web").first()
        if not web_channel:
            return

        position = Position.objects.filter(election=closed_election).first()
        if not position:
            return

        candidates = list(Candidate.objects.filter(election=closed_election, position=position)[:2])
        if len(candidates) < 2:
            candidates = [
                Candidate.objects.update_or_create(
                    election=closed_election,
                    full_name="Kwame Mensah",
                    defaults={
                        "position": position,
                        "department": "Information Technology",
                        "status": Candidate.Status.APPROVED,
                    },
                )[0],
                Candidate.objects.update_or_create(
                    election=closed_election,
                    full_name="Ama Osei",
                    defaults={
                        "position": position,
                        "department": "Computer Science",
                        "status": Candidate.Status.APPROVED,
                    },
                )[0],
            ]

        voters = list(
            User.objects.filter(role__name=Role.Name.STUDENT, is_active=True)[:5]
        )
        vote_ts = now - timedelta(days=54)
        for idx, voter in enumerate(voters):
            candidate = candidates[idx % len(candidates)]
            ts_iso = vote_ts.isoformat()
            vote_hash = Vote.compute_vote_hash(
                closed_election.pk,
                position.pk,
                candidate.pk,
                voter.pk,
                web_channel.pk,
                ts_iso,
            )
            Vote.objects.get_or_create(
                user=voter,
                position=position,
                candidate=candidate,
                defaults={
                    "election": closed_election,
                    "channel": web_channel,
                    "vote_hash": vote_hash,
                    "timestamp": vote_ts,
                },
            )

    def _seed_audit_logs(self, open_election, closed_election, student, admin, now):
        """Seed audit trail entries for security monitoring dashboards."""
        samples = [
            (AuditLog.EventType.LOGIN_SUCCESS, student, open_election, now - timedelta(hours=2)),
            (AuditLog.EventType.BALLOT_VIEWED, student, open_election, now - timedelta(hours=1)),
            (AuditLog.EventType.VOTE_CAST, student, closed_election, now - timedelta(days=54)),
            (AuditLog.EventType.ELECTION_STATUS_CHANGED, admin, open_election, now - timedelta(days=1)),
            (AuditLog.EventType.ADMIN_ACTION, admin, None, now - timedelta(hours=6)),
        ]
        for event_type, user, election, ts in samples:
            AuditLog.objects.get_or_create(
                user=user,
                event_type=event_type,
                timestamp=ts,
                defaults={
                    "election": election,
                    "ip_address": "196.216.0.1",
                    "metadata": {"demo": True, "source": "seed_demo_data"},
                },
            )

    def _seed_strongroom_custody(self, closed_election, admin, now):
        """Seed custody timeline and ballot seals for strongroom views."""
        seal = ElectionSeal.objects.filter(election=closed_election).first()
        if seal:
            CustodyRecord.objects.get_or_create(
                election=closed_election,
                action="election_sealed",
                timestamp=now - timedelta(days=51),
                defaults={
                    "actor": admin,
                    "entity_type": "election_seal",
                    "entity_uuid": seal.uuid,
                    "current_state": {"status": seal.status},
                    "metadata": {"demo": True},
                },
            )
            CustodyRecord.objects.get_or_create(
                election=closed_election,
                action="results_published",
                timestamp=now - timedelta(days=50),
                defaults={
                    "actor": admin,
                    "entity_type": "election_result",
                    "current_state": {"status": "published"},
                    "metadata": {"demo": True},
                },
            )

        voter = User.objects.filter(role__name=Role.Name.STUDENT).first()
        if voter:
            svt_id = uuid_mod.uuid4()
            vote_refs = [
                str(v.vote_id)
                for v in Vote.objects.filter(election=closed_election, user=voter)[:3]
            ]
            BallotSeal.objects.get_or_create(
                election=closed_election,
                user=voter,
                svt_id=svt_id,
                defaults={
                    "vote_references": vote_refs,
                    "vote_count": len(vote_refs) or 1,
                    "seal_hash": BallotSeal.compute_seal_hash(
                        closed_election.uuid, svt_id, vote_refs, []
                    ),
                    "status": BallotSeal.Status.SEALED,
                    "sealed_at": now - timedelta(days=53),
                },
            )

    def _seed_biometric_profiles(self):
        """Enroll privileged demo users for biometric login (mock inference)."""
        import base64
        import hashlib

        from django.conf import settings

        settings.BIOMETRICS_INFERENCE_MODE = "mock"

        from apps.biometrics.services.enrollment_service import biometric_enrollment_service
        from apps.system.models import FeatureFlag

        flag, _ = FeatureFlag.objects.get_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": False},
        )
        flag.enabled = getattr(settings, "BIOMETRIC_AUTH_ENABLED", False)
        flag.save(update_fields=["enabled"])

        super_admin = User.objects.filter(role__name=Role.Name.SUPER_ADMIN).first()
        if not super_admin:
            return

        def mock_image(seed: str) -> str:
            return base64.b64encode(hashlib.sha256(seed.encode()).digest()).decode()

        for user in User.objects.filter(role__name__in=[Role.Name.ADMIN, Role.Name.SUPER_ADMIN]):
            images = [mock_image(f"demo-{user.username}-{i}") for i in range(10)]
            try:
                biometric_enrollment_service.enroll(
                    actor=super_admin,
                    target_user=user,
                    images=images,
                    ip_address="127.0.0.1",
                )
                self.stdout.write(f"  + biometric profile for {user.username}")
            except Exception as exc:
                self.stdout.write(f"  ! biometric skip {user.username}: {exc}")
