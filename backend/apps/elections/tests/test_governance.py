"""Governance separation tests — Phase 29."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.elections.models import Election

User = get_user_model()


class GovernancePermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN, defaults={"description": "Admin"}
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN, defaults={"description": "Super Admin"}
        )
        self.admin = User.objects.create_user(
            email="admin@test.edu",
            password="testpass123",
            role=self.admin_role,
        )
        self.super_admin = User.objects.create_user(
            email="super@test.edu",
            password="testpass123",
            role=self.super_role,
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Governance Test Election",
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=Election.Status.DRAFT,
        )

    def test_super_admin_cannot_create_election(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.post(
            "/api/v1/elections/",
            {"title": "Blocked", "election_type": "general"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_election(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/elections/",
            {
                "title": "Allowed",
                "election_type": "general",
                "description": "Test",
            },
            format="json",
        )
        self.assertIn(response.status_code, {status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST})

    def test_super_admin_cannot_open_election(self):
        self.election.status = Election.Status.SCHEDULED
        self.election.save(update_fields=["status"])
        self.client.force_authenticate(self.super_admin)
        response = self.client.post(f"/api/v1/elections/{self.election.uuid}/open/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_read_elections(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/v1/elections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_campus_status_is_anonymous(self):
        response = self.client.get("/api/v1/elections/public/campus-status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("phase", response.data["data"])
