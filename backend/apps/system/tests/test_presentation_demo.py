from django.test import TestCase, override_settings

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.candidates.services.candidate_service import CandidateService
from apps.elections.models import Election, Position
from apps.system.services.presentation_demo_service import presentation_demo_service


@override_settings(DEBUG=True, DEV_BOOTSTRAP_PASSWORD="local-test-bootstrap-pass")
class PresentationDemoSeedTests(TestCase):
    def test_seed_creates_src_and_fassa_elections(self):
        summary = presentation_demo_service.seed()
        self.assertEqual(summary.student_count, 30)
        self.assertEqual(summary.src_election["votes"], 0)
        self.assertEqual(summary.src_election["status"], Election.Status.OPEN)
        self.assertGreater(summary.fassa_election["votes"], 0)
        self.assertEqual(summary.fassa_election["result_status"], "published")

    def test_demo_student_has_otp_fallback_flag(self):
        presentation_demo_service.seed()
        student = User.objects.get(index_number="BC/ITS/24/047")
        self.assertTrue(student.demo_seed)


class CandidateUserLinkTests(TestCase):
    def setUp(self):
        self.student_role = Role.objects.get(name=Role.Name.STUDENT)
        self.admin = User.objects.create_user(
            email="officer@ttu.edu.gh",
            password="local-test-officer-pass",
            username="officer",
            first_name="Demo",
            last_name="Officer",
            role=Role.objects.get(name=Role.Name.ADMIN),
            is_staff=True,
        )
        self.student = User.objects.create_user(
            email="student.link@ttu.edu.gh",
            password="unused",
            username="student.link",
            first_name="Linked",
            last_name="Student",
            role=self.student_role,
            index_number="BC/ITS/24/099",
            student_id="BC/ITS/24/099",
        )
        self.election = Election.objects.create(
            title="Linkage Test Election",
            election_type=Election.ElectionType.STUDENT_UNION,
            start_date="2026-07-01T08:00:00Z",
            end_date="2026-07-02T08:00:00Z",
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="President",
            display_order=0,
        )

    def test_create_candidate_links_existing_student(self):
        service = CandidateService()
        candidate = service.create_candidate(
            self.election.uuid,
            {
                "position_uuid": self.position.uuid,
                "user_uuid": self.student.uuid,
                "department": "Computer Science",
            },
        )
        self.assertEqual(candidate.user_id, self.student.id)
        self.assertEqual(candidate.full_name, "Linked Student")
