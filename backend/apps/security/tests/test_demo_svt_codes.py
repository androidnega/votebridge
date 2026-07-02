"""Tests for development demo SVT pool (VB-DEMO-0001 … VB-DEMO-0010)."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.security.demo_svt_codes import DEFAULT_DEMO_SVT_CODES, get_dev_demo_svt_codes
from apps.security.models import SVTToken
from apps.security.services.svt_service import svt_service
from core.exceptions import ValidationError
from tests.integration.fixtures import ensure_voting_channels


@override_settings(DEBUG=True, DEV_SVT_FALLBACK_ENABLED=True)
class DemoSVTCodeTests(TestCase):
    def setUp(self):
        ensure_voting_channels()
        admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="demo-svt-admin@ttu.edu.gh",
            password="unused",
            role=admin_role,
        )
        self.student = User.objects.create_user(
            email="demo-svt-student@ttu.edu.gh",
            password="unused",
            role=student_role,
            index_number="BC/ITS/24/048",
            phone_number="233241234568",
            first_name="Demo",
            last_name="Student",
        )
        self.other_student = User.objects.create_user(
            email="demo-svt-student2@ttu.edu.gh",
            password="unused",
            role=student_role,
            index_number="BC/ITS/24/049",
            phone_number="233241234569",
            first_name="Other",
            last_name="Student",
        )
        self.election_a = Election.objects.create(
            title="SRC Elections A",
            status=Election.Status.OPEN,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin,
        )
        self.election_b = Election.objects.create(
            title="SRC Elections B",
            status=Election.Status.OPEN,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin,
        )
        for election in (self.election_a, self.election_b):
            position = Position.objects.create(
                election=election,
                title="President",
                max_votes_allowed=1,
                is_active=True,
                is_votable=True,
            )
            Candidate.objects.create(
                election=election,
                position=position,
                full_name="Candidate One",
                department="CS",
                status=Candidate.Status.APPROVED,
            )
            VoterEligibility.objects.create(
                election=election,
                user=self.student,
                is_eligible=True,
            )
            VoterEligibility.objects.create(
                election=election,
                user=self.other_student,
                is_eligible=True,
            )

    def test_default_pool_has_ten_codes(self):
        self.assertEqual(len(DEFAULT_DEMO_SVT_CODES), 10)
        self.assertEqual(get_dev_demo_svt_codes()[0], "VB-DEMO-0001")
        self.assertEqual(get_dev_demo_svt_codes()[9], "VB-DEMO-0010")

    def test_demo_code_validates_without_prior_request(self):
        session = svt_service.validate_and_start_ballot(
            "VB-DEMO-0001",
            self.student,
            self.election_a.uuid,
        )
        self.assertEqual(session["status"], SVTToken.Status.VALIDATED)
        svt = SVTToken.objects.get(svt_id=session["svt_id"])
        self.assertEqual(svt.source_demo_code, "VB-DEMO-0001")
        self.assertGreater(svt.expires_at.year, 2090)

    @patch("apps.security.services.svt_service.SVTService._send_svt_sms")
    def test_terminal_issued_code_still_works(self, mock_sms):
        issued = svt_service.request_svt(self.election_a.uuid, self.student)
        session = svt_service.validate_and_start_ballot(
            issued["token_code"],
            self.student,
            self.election_a.uuid,
        )
        self.assertEqual(session["status"], SVTToken.Status.VALIDATED)
        mock_sms.assert_called_once()

    def test_demo_code_cannot_reuse_after_vote_in_other_election(self):
        demo_code = "VB-DEMO-0002"
        svt_a = svt_service.validate_and_start_ballot(
            demo_code,
            self.student,
            self.election_a.uuid,
        )
        svt_token = SVTToken.objects.get(svt_id=svt_a["svt_id"])
        svt_service.consume_svt(svt_token, self.student, vote_count=1)

        with self.assertRaises(ValidationError) as ctx:
            svt_service.validate_and_start_ballot(
                demo_code,
                self.student,
                self.election_b.uuid,
            )
        self.assertEqual(ctx.exception.code, "demo_svt_election_bound")

    def test_different_demo_code_works_on_second_election(self):
        svt_service.validate_and_start_ballot(
            "VB-DEMO-0003",
            self.student,
            self.election_a.uuid,
        )
        svt_a = SVTToken.objects.filter(
            user=self.student,
            election=self.election_a,
            source_demo_code="VB-DEMO-0003",
        ).first()
        svt_service.consume_svt(svt_a, self.student, vote_count=1)

        session_b = svt_service.validate_and_start_ballot(
            "VB-DEMO-0004",
            self.student,
            self.election_b.uuid,
        )
        self.assertEqual(session_b["status"], SVTToken.Status.VALIDATED)

    def test_same_demo_code_can_be_used_by_different_students(self):
        session_one = svt_service.validate_and_start_ballot(
            "VB-DEMO-0005",
            self.student,
            self.election_a.uuid,
        )
        session_two = svt_service.validate_and_start_ballot(
            "VB-DEMO-0005",
            self.other_student,
            self.election_a.uuid,
        )
        self.assertNotEqual(session_one["svt_id"], session_two["svt_id"])

    @override_settings(DEBUG=False)
    def test_demo_codes_disabled_outside_debug(self):
        with self.assertRaises(ValidationError):
            svt_service.validate_and_start_ballot(
                "VB-DEMO-0001",
                self.student,
                self.election_a.uuid,
            )
