"""Election readiness validator tests (RC2)."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.elections.services import election_readiness_service, election_service
from apps.system.models import FeatureFlag
from core.exceptions import ValidationError


def _ready_health():
    return {
        "overall_status": "healthy",
        "checked_at": timezone.now().isoformat(),
        "components": [
            {"name": "database", "status": "healthy", "details": "OK"},
            {"name": "redis", "status": "healthy", "details": "OK"},
            {"name": "websockets", "status": "healthy", "details": "OK"},
            {"name": "communications", "status": "healthy", "details": "OK"},
            {"name": "ussd", "status": "healthy", "details": "OK"},
        ],
    }


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class ElectionReadinessServiceTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.admin = User.objects.create_user(
            email="readiness-admin@test.local",
            username="readiness-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT, defaults={"description": "Student"})
        self.student = User.objects.create_user(
            email="readiness-student@test.local",
            username="readiness-student",
            password="1234",
            index_number="BC/ICT/24/056",
            role=self.student_role,
        )
        FeatureFlag.objects.update_or_create(
            key="fraud_detection",
            defaults={"name": "Fraud Detection", "description": "", "enabled": True},
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Readiness Test Election",
            election_type=Election.ElectionType.STUDENT_UNION,
            start_date=now + timedelta(hours=1),
            end_date=now + timedelta(days=2),
            status=Election.Status.SCHEDULED,
            allow_web_voting=True,
            allow_ussd_voting=True,
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="President",
            is_active=True,
        )
        Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Candidate A",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=True,
            verified_by=self.admin,
            verified_at=now,
        )

    @patch("apps.elections.services.election_readiness_service.OperationsHealthService.check_all")
    @patch(
        "apps.strongroom.services.integrity_verification_service.integrity_verification_service.get_dashboard"
    )
    def test_ready_election_scores_high(self, mock_dashboard, mock_health):
        mock_health.return_value = _ready_health()
        mock_dashboard.return_value = {"seal_status": "pending"}
        report = election_readiness_service.assess(self.election, actor=self.admin)
        self.assertTrue(report.is_ready)
        self.assertGreaterEqual(report.readiness_score, 80)
        self.assertIn("ballot_structure", report.checks)

    @patch("apps.elections.services.election_readiness_service.OperationsHealthService.check_all")
    def test_missing_eligible_voters_blocks_open(self, mock_health):
        mock_health.return_value = _ready_health()
        VoterEligibility.objects.all().delete()
        report = election_readiness_service.assess(self.election)
        self.assertFalse(report.is_ready)
        self.assertIn("eligible voter", report.blocking_issues[0].lower())

    @patch("apps.elections.services.election_readiness_service.OperationsHealthService.check_all")
    @patch(
        "apps.strongroom.services.integrity_verification_service.integrity_verification_service.get_dashboard"
    )
    def test_open_election_blocked_when_not_ready(self, mock_dashboard, mock_health):
        mock_health.return_value = _ready_health()
        mock_dashboard.return_value = {"seal_status": "pending"}
        VoterEligibility.objects.all().delete()
        with self.assertRaises(ValidationError):
            election_service.open_election(self.election.uuid, actor=self.admin)

    @patch("apps.elections.services.election_readiness_service.OperationsHealthService.check_all")
    @patch(
        "apps.strongroom.services.integrity_verification_service.integrity_verification_service.get_dashboard"
    )
    def test_open_election_succeeds_when_ready(self, mock_dashboard, mock_health):
        mock_health.return_value = _ready_health()
        mock_dashboard.return_value = {"seal_status": "pending"}
        opened = election_service.open_election(self.election.uuid, actor=self.admin)
        self.assertEqual(opened.status, Election.Status.OPEN)


class ElectionReadinessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.admin = User.objects.create_user(
            email="readiness-api-admin@test.local",
            username="readiness-api-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="API Readiness Election",
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(hours=2),
            end_date=now + timedelta(days=3),
            status=Election.Status.SCHEDULED,
            allow_web_voting=True,
            created_by=self.admin,
        )
        FeatureFlag.objects.update_or_create(
            key="fraud_detection",
            defaults={"name": "Fraud Detection", "description": "", "enabled": True},
        )

    @patch("apps.elections.services.election_readiness_service.OperationsHealthService.check_all")
    def test_readiness_endpoint_returns_report(self, mock_health):
        mock_health.return_value = _ready_health()
        self.client.force_authenticate(user=self.admin)
        url = reverse("elections:election-readiness", kwargs={"uuid": self.election.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertIn("readiness_score", data)
        self.assertIn("checks", data)
