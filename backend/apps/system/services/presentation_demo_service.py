"""Presentation-ready demo seed — TTU SRC live election + FASSA historical results."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.accounts.utils.phone import normalize_phone
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility, VotingChannel
from apps.elections.services import election_service
from apps.notifications.models import InAppNotification
from apps.results.models import ElectionResult
from apps.results.services.certification_service import certification_service
from apps.results.services.results_service import results_generation_service
from apps.security.models import AuditLog, SVTToken
from apps.strongroom.models import CustodyRecord, ElectionSeal
from apps.strongroom.services.vault_committee_service import vault_committee_service
from apps.system.data.presentation_demo_data import (
    DEMO_OTP_FALLBACK,
    DEMO_SVT_FALLBACK,
    DEMO_STAFF_PASSWORD,
    FASSA_CANDIDATE_ROSTER,
    FASSA_ELECTION_TITLE,
    FASSA_HOURLY_VOTE_WEIGHTS,
    FASSA_POSITIONS,
    SRC_CANDIDATE_ROSTER,
    SRC_ELECTION_TITLE,
    SRC_POSITIONS,
    STAFF_ACCOUNTS,
    STRONGROOM_CUSTODIAN_USERNAMES,
    TTU_DEMO_STUDENTS,
)
from apps.system.services.dev_reset_service import dev_reset_service
from apps.system.services.feature_flag_service import feature_flag_service
from apps.system.services.system_service import system_settings_service
from apps.voting.models import Vote

logger = logging.getLogger("votebridge")

PROJECT_ROOT = Path(settings.BASE_DIR).resolve().parent


@dataclass
class PresentationSeedSummary:
    cleared: dict = field(default_factory=dict)
    staff_accounts: list = field(default_factory=list)
    student_count: int = 0
    src_election: dict = field(default_factory=dict)
    fassa_election: dict = field(default_factory=dict)
    strongroom: dict = field(default_factory=dict)
    demo_otp_fallback: str = DEMO_OTP_FALLBACK
    demo_svt_fallback: str = DEMO_SVT_FALLBACK


class PresentationDemoService:
    @transaction.atomic
    def seed(self) -> PresentationSeedSummary:
        summary = PresentationSeedSummary()
        reset_summary = dev_reset_service.clear_operational_data()
        summary.cleared = reset_summary.cleared

        self._ensure_platform_readiness()

        users_by_index = {}
        users_by_username = {}

        for account in STAFF_ACCOUNTS:
            user = self._create_staff(account)
            users_by_username[user.username] = user
            summary.staff_accounts.append(
                {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.name,
                    "phone_number": user.phone_number,
                    "password": account["password"],
                    "otp_fallback": DEMO_OTP_FALLBACK,
                }
            )

        phone_base = 257940801
        for idx, row in enumerate(TTU_DEMO_STUDENTS):
            user = self._create_student(row, phone_base + idx)
            users_by_index[user.index_number] = user
        summary.student_count = len(users_by_index)

        admin = users_by_username["admin"]
        super_admin = users_by_username["superadmin"]

        src = self._build_src_election(admin, users_by_index)
        summary.strongroom = self._seed_strongroom(src, admin, super_admin, users_by_username)
        src_open = self._open_src_election(src["uuid"], admin)
        summary.src_election = {**src, **src_open}

        fassa = self._seed_fassa_election(admin, super_admin, users_by_index)
        summary.fassa_election = fassa

        self._seed_welcome_notifications(users_by_index)
        return summary

    def _ensure_platform_readiness(self) -> None:
        system_settings_service.ensure_defaults()
        feature_flag_service.ensure_defaults()
        for channel_name in (
            VotingChannel.ChannelName.WEB,
            VotingChannel.ChannelName.USSD,
            VotingChannel.ChannelName.SMS,
        ):
            VotingChannel.objects.update_or_create(
                channel_name=channel_name,
                defaults={"is_active": True},
            )

    def _create_staff(self, spec: dict) -> User:
        role = Role.objects.get(name=spec["role"])
        phone = normalize_phone(spec.get("phone_number", "")) or spec.get("phone_number", "")
        user, _ = User.objects.update_or_create(
            email=spec["email"],
            defaults={
                "username": spec["username"],
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
                "role": role,
                "phone_number": phone,
                "is_verified": True,
                "is_staff": spec.get("is_staff", False),
                "is_superuser": spec.get("is_superuser", False),
                "is_active": True,
                "demo_seed": True,
            },
        )
        user.set_password(spec["password"])
        user.save()
        return user

    def _create_student(self, row, phone_number: int) -> User:
        first, last, index, email, department, role_name = row
        role = Role.objects.get(name=role_name)
        phone = normalize_phone(str(phone_number)) or str(phone_number)
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": first,
                "last_name": last,
                "index_number": index,
                "student_id": index,
                "role": role,
                "phone_number": phone,
                "is_verified": True,
                "is_active": True,
                "demo_seed": True,
            },
        )
        user.set_unusable_password()
        user.save()
        return user

    def _build_src_election(self, admin, users_by_index) -> dict:
        now = timezone.now()
        election, _ = Election.objects.update_or_create(
            title=SRC_ELECTION_TITLE,
            defaults={
                "description": "Takoradi Technical University Student Representative Council elections.",
                "election_type": Election.ElectionType.STUDENT_UNION,
                "start_date": now,
                "end_date": now + timedelta(days=1),
                "status": Election.Status.DRAFT,
                "allow_web_voting": True,
                "allow_ussd_voting": True,
                "allow_sms_notifications": False,
                "demo_seed": True,
                "created_by_system": True,
                "created_by": admin,
            },
        )

        positions = {}
        for order, title in enumerate(SRC_POSITIONS):
            position, _ = Position.objects.update_or_create(
                election=election,
                title=title,
                defaults={
                    "display_order": order,
                    "max_votes_allowed": 1,
                    "is_active": True,
                    "is_votable": True,
                },
            )
            positions[title] = position

        candidate_count = 0
        for pos_title, roster in SRC_CANDIDATE_ROSTER.items():
            position = positions[pos_title]
            for full_name, department, index, image_file in roster:
                linked_user = users_by_index.get(index) if index else None
                candidate, _ = Candidate.objects.update_or_create(
                    election=election,
                    full_name=full_name,
                    defaults={
                        "position": position,
                        "department": department,
                        "manifesto": "Committed to transparent SRC leadership and student welfare.",
                        "status": Candidate.Status.APPROVED,
                        "user": linked_user,
                    },
                )
                if image_file:
                    self._attach_candidate_image(candidate, image_file)
                candidate_count += 1

        eligible = self._sync_eligibility(election, admin, users_by_index.values())
        election = election_service.schedule_election(election.uuid)

        return {
            "title": election.title,
            "uuid": str(election.uuid),
            "status": election.status,
            "start_date": election.start_date.isoformat(),
            "end_date": election.end_date.isoformat(),
            "positions": len(positions),
            "candidates": candidate_count,
            "eligible_voters": eligible,
            "votes": 0,
        }

    def _open_src_election(self, election_uuid, admin) -> dict:
        election = election_service.open_election(election_uuid, actor=admin)
        Vote.objects.filter(election=election).delete()
        return {
            "status": election.status,
            "votes": 0,
        }

    def _seed_fassa_election(self, admin, super_admin, users_by_index) -> dict:
        now = timezone.now()
        start = now - timedelta(days=45)
        end = now - timedelta(days=44)

        election, _ = Election.objects.update_or_create(
            title=FASSA_ELECTION_TITLE,
            defaults={
                "description": "Faculty of Applied Sciences Student Association elections — 2025 cycle.",
                "election_type": Election.ElectionType.FACULTY,
                "start_date": start,
                "end_date": end,
                "status": Election.Status.CLOSED,
                "allow_web_voting": True,
                "allow_ussd_voting": True,
                "demo_seed": True,
                "created_by": admin,
            },
        )

        positions = {}
        for order, title in enumerate(FASSA_POSITIONS):
            position, _ = Position.objects.update_or_create(
                election=election,
                title=title,
                defaults={
                    "display_order": order,
                    "max_votes_allowed": 1,
                    "is_active": True,
                    "is_votable": True,
                },
            )
            positions[title] = position

        candidate_count = 0
        for pos_title, roster in FASSA_CANDIDATE_ROSTER.items():
            position = positions[pos_title]
            for full_name, department, index, image_file in roster:
                linked_user = users_by_index.get(index) if index else None
                candidate, _ = Candidate.objects.update_or_create(
                    election=election,
                    full_name=full_name,
                    defaults={
                        "position": position,
                        "department": department,
                        "manifesto": "Serving the Faculty of Applied Sciences with integrity.",
                        "status": Candidate.Status.APPROVED,
                        "user": linked_user,
                    },
                )
                if image_file:
                    self._attach_candidate_image(candidate, image_file)
                candidate_count += 1

        students = list(users_by_index.values())
        eligible = self._sync_eligibility(election, admin, students)

        vote_count = self._seed_historical_votes(election, positions, now - timedelta(days=44))
        self._seed_fassa_audit_logs(election, admin, students[0] if students else None)

        result = results_generation_service.generate_results(election.uuid, actor=admin)
        if result.status == ElectionResult.Status.GENERATED:
            result.status = ElectionResult.Status.PENDING_CERTIFICATION
            result.save(update_fields=["status"])
        result = certification_service.certify(election.uuid, super_admin, acknowledge_fraud=True)
        result = certification_service.publish(election.uuid, super_admin)

        ElectionSeal.objects.update_or_create(
            election=election,
            defaults={
                "election_result": result,
                "election_seal_hash": election.uuid.hex[:64],
                "verification_hash": result.uuid.hex[:64],
                "ballot_seals_digest": "presentation-fassa-digest",
                "sealed_by": super_admin,
                "sealed_at": now - timedelta(days=42),
                "status": ElectionSeal.Status.SEALED,
            },
        )
        CustodyRecord.objects.get_or_create(
            election=election,
            action="results_published",
            defaults={
                "actor": super_admin,
                "previous_state": {"status": "certified"},
                "current_state": {"status": "published"},
                "metadata": {"demo": True},
            },
        )

        return {
            "title": election.title,
            "uuid": str(election.uuid),
            "status": election.status,
            "result_status": result.status,
            "positions": len(positions),
            "candidates": candidate_count,
            "eligible_voters": eligible,
            "votes": vote_count,
            "turnout_percentage": float(result.turnout_percentage),
            "distinct_voters": result.integrity_report.get("distinct_voters")
            if isinstance(result.integrity_report, dict)
            else None,
        }

    def _sync_eligibility(self, election, admin, users) -> int:
        count = 0
        now = timezone.now()
        for user in users:
            if user.role.name not in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
                continue
            VoterEligibility.objects.update_or_create(
                election=election,
                user=user,
                defaults={
                    "is_eligible": True,
                    "eligibility_reason": "TTU demo voter roll",
                    "verified_by": admin,
                    "verified_at": now,
                },
            )
            count += 1
        return count

    def _seed_historical_votes(self, election, positions: dict, base_time) -> int:
        from django.contrib.auth.hashers import make_password

        web = VotingChannel.objects.get(channel_name=VotingChannel.ChannelName.WEB)
        ussd = VotingChannel.objects.get(channel_name=VotingChannel.ChannelName.USSD)
        students = list(
            User.objects.filter(
                demo_seed=True,
                role__name__in=[Role.Name.STUDENT, Role.Name.CANDIDATE],
                is_active=True,
            ).order_by("index_number")
        )
        if not students:
            return 0

        position_list = list(positions.values())
        vote_total = 0
        voted_pairs: set[tuple[int, int]] = set()
        user_svts: dict[int, SVTToken] = {}

        for hour_idx, weight in enumerate(FASSA_HOURLY_VOTE_WEIGHTS):
            bucket = (base_time + timedelta(hours=hour_idx)).replace(minute=0, second=0, microsecond=0)
            for slot in range(weight):
                student = students[vote_total % len(students)]
                position = position_list[vote_total % len(position_list)]
                pair = (student.pk, position.pk)
                if pair in voted_pairs:
                    vote_total += 1
                    continue

                candidates = list(
                    Candidate.objects.filter(
                        election=election,
                        position=position,
                        status=Candidate.Status.APPROVED,
                    )
                )
                if not candidates:
                    vote_total += 1
                    continue

                if student.pk not in user_svts:
                    issued_at = bucket - timedelta(minutes=5)
                    svt = SVTToken.objects.create(
                        user=student,
                        election=election,
                        token_code=make_password(f"demo-svt-{student.pk}-{election.pk}"),
                        issued_at=issued_at,
                        expires_at=bucket + timedelta(hours=2),
                        validated_at=issued_at + timedelta(minutes=2),
                        used_at=bucket + timedelta(minutes=3),
                        status=SVTToken.Status.USED,
                    )
                    user_svts[student.pk] = svt

                svt = user_svts[student.pk]
                candidate = candidates[vote_total % len(candidates)]
                channel = ussd if vote_total % 5 == 0 else web
                timestamp = bucket + timedelta(minutes=3 + (slot * 3) % 50)
                vote_hash = Vote.compute_vote_hash(
                    election.pk,
                    position.pk,
                    candidate.pk,
                    student.pk,
                    channel.pk,
                    timestamp.isoformat(),
                )
                Vote.objects.create(
                    election=election,
                    position=position,
                    candidate=candidate,
                    user=student,
                    channel=channel,
                    svt_id=svt.svt_id,
                    vote_hash=vote_hash,
                    timestamp=timestamp,
                )
                voted_pairs.add(pair)
                vote_total += 1

        return vote_total

    def _seed_strongroom(self, election_ref: dict, admin, super_admin, users_by_username) -> dict:
        from apps.elections.repositories.election_repository import ElectionRepository

        election = ElectionRepository().get_by_uuid(election_ref["uuid"])
        if not election:
            return {}

        custodians = [
            users_by_username[name]
            for name in STRONGROOM_CUSTODIAN_USERNAMES
            if name in users_by_username
        ]
        if len(custodians) < 2:
            return {"configured": False}

        vault_committee_service.configure_committee(
            election,
            actor=admin,
            member_user_uuids=[str(u.uuid) for u in custodians],
            session_duration_hours=2,
        )
        vault_committee_service.submit_for_approval(election, actor=admin)
        committee = vault_committee_service.approve_committee(election, actor=super_admin)

        return {
            "configured": True,
            "election": election.title,
            "custodians": [
                {
                    "username": u.username,
                    "email": u.email,
                    "password": DEMO_STAFF_PASSWORD,
                    "otp_fallback": DEMO_OTP_FALLBACK,
                }
                for u in custodians
            ],
            "status": committee.get("status"),
        }

    def _seed_fassa_audit_logs(self, election, admin, student) -> None:
        AuditLog.objects.get_or_create(
            election=election,
            event_type=AuditLog.EventType.ELECTION_STATUS_CHANGED,
            defaults={
                "user": admin,
                "metadata": {"demo": True, "status": "closed", "note": "FASSA election closed for counting."},
            },
        )
        AuditLog.objects.get_or_create(
            election=election,
            event_type=AuditLog.EventType.BALLOT_SUBMITTED,
            defaults={
                "user": student or admin,
                "metadata": {"demo": True, "note": "Demo ballot submitted during FASSA 2025."},
            },
        )
        if student:
            AuditLog.objects.get_or_create(
                election=election,
                event_type=AuditLog.EventType.VOTE_CAST,
                defaults={
                    "user": student,
                    "metadata": {"demo": True, "note": "Demo vote recorded during FASSA 2025."},
                },
            )

    def _seed_welcome_notifications(self, users_by_index) -> None:
        for user in users_by_index.values():
            InAppNotification.objects.get_or_create(
                user=user,
                title="Welcome to VoteBridge",
                defaults={
                    "body": "TTU demo environment is ready. Check Elections for the active SRC ballot.",
                    "category": "system",
                    "metadata": {"demo": True},
                },
            )
            InAppNotification.objects.get_or_create(
                user=user,
                title="SRC elections are open",
                defaults={
                    "body": f"{SRC_ELECTION_TITLE} is now open for voting.",
                    "category": "election",
                    "metadata": {"demo": True, "election_title": SRC_ELECTION_TITLE},
                },
            )

    def _attach_candidate_image(self, candidate: Candidate, filename: str) -> None:
        path = PROJECT_ROOT / "frontend" / "public" / "candidates" / filename
        if not path.is_file():
            logger.warning("Candidate image not found: %s", path)
            return
        with path.open("rb") as handle:
            candidate.image.save(filename, File(handle), save=True)


presentation_demo_service = PresentationDemoService()
