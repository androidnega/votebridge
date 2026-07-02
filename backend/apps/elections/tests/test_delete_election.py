"""Tests for election deletion (draft/scheduled only)."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.elections.models import Election, Position
from apps.elections.services import election_service

User = get_user_model()


class ElectionDeleteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.admin = User.objects.create_user(
            email="delete-admin@test.edu",
            password="testpass123",
            role=self.admin_role,
        )
        now = timezone.now()
        self.draft = Election.objects.create(
            title="Draft To Delete",
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=3),
            status=Election.Status.DRAFT,
        )
        Position.objects.create(
            election=self.draft,
            title="President",
            max_votes_allowed=1,
        )
        self.open_election = Election.objects.create(
            title="Open Election",
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(days=1),
            status=Election.Status.OPEN,
        )

    def test_admin_can_delete_draft_election(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f"/api/v1/elections/{self.draft.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Election.objects.filter(uuid=self.draft.uuid).exists())

    def test_admin_cannot_delete_open_election(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f"/api/v1/elections/{self.open_election.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Election.objects.filter(uuid=self.open_election.uuid).exists())

    def test_service_delete_scheduled_election(self):
        now = timezone.now()
        scheduled = Election.objects.create(
            title="Scheduled Remove",
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=Election.Status.SCHEDULED,
        )
        election_service.delete_election(scheduled.uuid)
        self.assertFalse(Election.objects.filter(uuid=scheduled.uuid).exists())
