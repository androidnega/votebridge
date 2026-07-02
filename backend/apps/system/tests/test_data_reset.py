"""Super-admin operational data reset tests."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.elections.models import Election
from apps.system.services.data_reset_service import RESET_CONFIRMATION_PHRASE, data_reset_service

User = get_user_model()


@override_settings(DEBUG=False)
class OperationalDataResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        self.admin = User.objects.create_user(
            email="reset-admin@test.edu",
            password="testpass123",
            role=self.admin_role,
        )
        self.super_admin = User.objects.create_user(
            email="reset-super@test.edu",
            password="testpass123",
            role=self.super_role,
        )
        now = timezone.now()
        Election.objects.create(
            title="Reset Target",
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=Election.Status.DRAFT,
        )

    @override_settings(DEBUG=True)
    def test_service_reset_clears_elections(self):
        summary = data_reset_service.reset_operational_data(
            actor=self.super_admin,
            confirmation=RESET_CONFIRMATION_PHRASE,
        )
        self.assertEqual(summary["elections_removed"], 1)
        self.assertEqual(Election.objects.count(), 0)

    def test_admin_cannot_reset_operational_data(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/system/data-reset/",
            {
                "confirmation": RESET_CONFIRMATION_PHRASE,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
