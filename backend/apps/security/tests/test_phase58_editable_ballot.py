"""Phase 58 — editable ballot selections remain temporary until final submit."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.security.services.svt_service import svt_service
from apps.voting.models import Vote
from apps.voting.services.vote_service import VoteService
from tests.integration.fixtures import ensure_voting_channels


class Phase58EditableBallotTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="phase58-admin@ttu.edu.gh",
            password="unused",
            role=admin_role,
        )
        self.student = User.objects.create_user(
            email="phase58-student@ttu.edu.gh",
            password="unused",
            role=student_role,
            phone_number="233241234567",
        )
        self.election = Election.objects.create(
            title="SRC General Elections 2026",
            status=Election.Status.OPEN,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="President",
            max_votes_allowed=1,
            is_active=True,
            is_votable=True,
        )
        self.candidate_a = Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Candidate A",
            status=Candidate.Status.APPROVED,
        )
        self.candidate_b = Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Candidate B",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
        )

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_no_votes_until_final_submit(self, mock_sms):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election.uuid,
        )
        self.assertEqual(Vote.objects.filter(user=self.student, election=self.election).count(), 0)

        vote_service = VoteService()
        vote_service.submit_ballot(
            self.election.uuid,
            self.student,
            issued["token_code"],
            selections=[
                {
                    "position_uuid": str(self.position.uuid),
                    "candidate_uuids": [str(self.candidate_b.uuid)],
                }
            ],
            channel_name="web",
        )
        self.assertEqual(Vote.objects.filter(user=self.student, election=self.election).count(), 1)
        vote = Vote.objects.get(user=self.student, election=self.election)
        self.assertEqual(vote.candidate_id, self.candidate_b.id)
