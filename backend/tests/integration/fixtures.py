"""Shared fixtures for Phase 22 integration tests."""

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility, VotingChannel


def ensure_voting_channels():
    for name in ("web", "ussd", "sms"):
        VotingChannel.objects.get_or_create(channel_name=name, defaults={"is_active": True})


def create_roles():
    roles = {}
    for name, desc in (
        (Role.Name.STUDENT, "Student"),
        (Role.Name.ADMIN, "Admin"),
        (Role.Name.SUPER_ADMIN, "Super Admin"),
    ):
        roles[name], _ = Role.objects.get_or_create(name=name, defaults={"description": desc})
    return roles


def create_test_users(roles):
    admin = User.objects.create_user(
        email="phase22-admin@test.local",
        username="phase22-admin",
        password="TestPass123!",
        role=roles[Role.Name.ADMIN],
    )
    student = User.objects.create_user(
        email="phase22-student@test.local",
        username="phase22-student",
        password="1234",
        index_number="BC/ITD/24/031",
        phone_number="233241234567",
        role=roles[Role.Name.STUDENT],
    )
    return admin, student


def create_open_ussd_election(*, admin, student, title="Phase 22 USSD Election"):
    ensure_voting_channels()
    now = timezone.now()
    election = Election.objects.create(
        title=title,
        description="Integration test election",
        election_type=Election.ElectionType.STUDENT_UNION,
        start_date=now - timedelta(hours=1),
        end_date=now + timedelta(days=7),
        status=Election.Status.OPEN,
        allow_web_voting=True,
        allow_ussd_voting=True,
        created_by=admin,
    )
    position = Position.objects.create(
        election=election,
        title="President",
        max_votes_allowed=1,
        display_order=1,
        is_active=True,
    )
    Candidate.objects.create(
        election=election,
        position=position,
        full_name="Kwame Mensah",
        status=Candidate.Status.APPROVED,
    )
    Candidate.objects.create(
        election=election,
        position=position,
        full_name="Ama Osei",
        status=Candidate.Status.APPROVED,
    )
    VoterEligibility.objects.create(
        election=election,
        user=student,
        is_eligible=True,
        verified_by=admin,
        verified_at=now,
    )
    return election, position
