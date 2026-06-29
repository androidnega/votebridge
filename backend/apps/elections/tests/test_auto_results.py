"""Tests for automatic results generation on election close — Phase 30."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.candidates.models import Candidate
from apps.elections.models import Election, Position, VoterEligibility
from apps.elections.services import election_service
from apps.results.models import ElectionResult

User = get_user_model()


class AutoResultsPipelineTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN, defaults={"description": "Admin"}
        )
        self.admin = User.objects.create_user(
            email="auto-results-admin@test.local",
            username="auto-results-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Auto Results Election",
            election_type=Election.ElectionType.GENERAL,
            start_date=now - timedelta(hours=2),
            end_date=now + timedelta(hours=4),
            status=Election.Status.OPEN,
            allow_web_voting=True,
            created_by=self.admin,
        )
        self.position = Position.objects.create(
            election=self.election,
            title="President",
            max_votes_allowed=1,
            display_order=1,
            is_active=True,
        )
        Candidate.objects.create(
            election=self.election,
            position=self.position,
            full_name="Test Candidate",
            status=Candidate.Status.APPROVED,
        )
        VoterEligibility.objects.create(
            election=self.election,
            user=self.admin,
            is_eligible=True,
            verified_by=self.admin,
            verified_at=now,
        )

    def test_close_election_auto_generates_results(self):
        closed = election_service.close_election(self.election.uuid)
        self.assertEqual(closed.status, Election.Status.CLOSED)
        result = ElectionResult.objects.get(election=self.election)
        self.assertIn(
            result.status,
            {
                ElectionResult.Status.PENDING_CERTIFICATION,
                ElectionResult.Status.GENERATED,
            },
        )
        self.assertIsNotNone(result.generated_at)

    def test_admin_cannot_manually_generate_results(self):
        self.election.status = Election.Status.CLOSED
        self.election.save(update_fields=["status"])
        ElectionResult.objects.create(
            election=self.election,
            status=ElectionResult.Status.PENDING_GENERATION,
        )
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.post(f"/api/v1/results/elections/{self.election.uuid}/generate/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_portal_endpoint(self):
        client = APIClient()
        response = client.get("/api/v1/elections/public/portal/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["data"]
        self.assertIn("phase", data)
        self.assertIn("timeline", data)
        self.assertIn("candidates", data)
