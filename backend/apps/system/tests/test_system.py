from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User


class SystemControlAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.super_admin = User.objects.create_user(
            email="scc-super@test.local",
            username="scc-super",
            password="TestPass123!",
            first_name="SCC",
            last_name="Super",
            role=self.super_role,
        )
        self.admin = User.objects.create_user(
            email="scc-admin@test.local",
            username="scc-admin",
            password="TestPass123!",
            first_name="SCC",
            last_name="Admin",
            role=self.admin_role,
        )
        self.overview_url = reverse("system:overview")

    def test_admin_cannot_access_overview(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_access_overview(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertIn("application_version", data)
        self.assertIn("platform_state", data)
        self.assertNotIn("active_election", data)
        self.assertIn("primary", data["platform_state"])
        self.assertIn("admin_activity", data)

    def test_public_branding_is_open(self):
        response = self.client.get(reverse("system:public-branding"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemSettingsServiceTests(TestCase):
    def test_default_settings_seeded(self):
        from apps.system.services.system_service import system_settings_service

        system_settings_service.ensure_defaults()
        auth_settings = system_settings_service.get_category("authentication")
        self.assertTrue(any(s["key"].endswith("jwt_access_minutes") for s in auth_settings))
