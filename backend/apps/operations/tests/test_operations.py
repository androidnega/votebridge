from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.operations.services.operations_service import (
    operations_dashboard_service,
    operations_health_service,
)


class OperationsAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.student_role, _ = Role.objects.get_or_create(
            name=Role.Name.STUDENT,
            defaults={"description": "Student"},
        )
        self.admin = User.objects.create_user(
            email="ops-admin@test.local",
            username="ops-admin",
            password="TestPass123!",
            first_name="Ops",
            last_name="Admin",
            role=self.admin_role,
        )
        self.student = User.objects.create_user(
            email="ops-student@test.local",
            username="ops-student",
            password="TestPass123!",
            first_name="Ops",
            last_name="Student",
            role=self.student_role,
        )
        self.overview_url = reverse("operations:overview")
        self.activity_url = reverse("operations:activity")

    def test_student_cannot_access_overview(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_overview(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertIn("system_health", data)
        self.assertIn("elections", data)
        self.assertIn("realtime", data)
        self.assertIn("pending_workloads", data)

    def test_invalid_activity_category_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.activity_url, {"category": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OperationsServiceTests(TestCase):
    def test_health_check_returns_components(self):
        payload = operations_health_service.check_all()
        self.assertIn("overall_status", payload)
        self.assertIn("components", payload)
        names = {c["name"] for c in payload["components"]}
        self.assertIn("database", names)
        self.assertIn("redis", names)

    def test_overview_composes_without_error(self):
        payload = operations_dashboard_service.get_overview()
        self.assertIn("elections", payload)
        self.assertIn("communications_summary", payload)
