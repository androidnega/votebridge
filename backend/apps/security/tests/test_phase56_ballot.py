"""
Phase 56 — Enterprise ballot experience & secure voting session tests.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.security.models import SVTToken
from apps.security.services.svt_service import svt_service
from apps.voting.services.vote_service import BallotService, VoteService
from core.utils.phone import mask_phone_number
from tests.integration.fixtures import ensure_voting_channels


class Phase56SVTTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="phase56-admin@ttu.edu.gh",
            password="unused",
            role=admin_role,
        )
        self.student = User.objects.create_user(
            email="phase56-student@ttu.edu.gh",
            password="unused",
            role=student_role,
            index_number="BC/ITS/24/099",
            phone_number="233241234567",
            first_name="Phase",
            last_name="Student",
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
        self.candidate = Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Ama Serwaa",
            department="Computer Science",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
        )

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_request_svt_uses_formatted_code_and_masks_phone(self, mock_sms):
        result = svt_service.request_svt(self.election.uuid, self.student)
        self.assertRegex(result["token_code"], r"^VB-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}$")
        self.assertEqual(len(result["masked_phone"]), len(mask_phone_number(self.student.phone_number)))
        mock_sms.assert_called_once()

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_validate_starts_ballot_session(self, mock_sms):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        session = svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election.uuid,
        )
        self.assertEqual(session["status"], SVTToken.Status.VALIDATED)
        self.assertIsNotNone(session["validated_at"])

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_single_transaction_submit_with_skipped_positions(self, mock_sms):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election.uuid,
        )
        vote_service = VoteService()
        confirmation = vote_service.submit_ballot(
            self.election.uuid,
            self.student,
            issued["token_code"],
            selections=[
                {"position_uuid": str(self.position.uuid), "candidate_uuids": [str(self.candidate.uuid)]},
            ],
            channel_name="web",
        )
        self.assertTrue(confirmation["confirmation_reference"].startswith("VTB-"))
        self.assertEqual(confirmation["positions_count"], 1)
        svt = SVTToken.objects.get(user=self.student, election=self.election)
        self.assertEqual(svt.status, SVTToken.Status.USED)

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_cannot_request_svt_after_submit(self, mock_sms):
        issued = svt_service.request_svt(self.election.uuid, self.student)
        svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election.uuid,
        )
        VoteService().submit_ballot(
            self.election.uuid,
            self.student,
            issued["token_code"],
            selections=[
                {"position_uuid": str(self.position.uuid), "candidate_uuids": [str(self.candidate.uuid)]},
            ],
            channel_name="web",
        )
        from core.exceptions import ConflictError

        with self.assertRaises(ConflictError):
            svt_service.request_svt(self.election.uuid, self.student)

    def test_ballot_payload_includes_session_flags(self):
        ballot = BallotService().get_ballot(self.election.uuid, self.student)
        self.assertIn("masked_phone", ballot)
        self.assertIn("ballot_session_active", ballot)
