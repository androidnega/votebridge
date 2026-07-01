from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.accounts.services.auth_service import AuthService
from core.exceptions import AuthenticationError


class Phase55AuthTests(TestCase):
    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(
            name=Role.Name.STUDENT,
            defaults={"description": "Student"},
        )
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.student = User.objects.create_user(
            email="student@ttu.edu.gh",
            password="StudentPass123!",
            index_number="BC/ITS/24/047",
            phone_number="233241234567",
            role=self.student_role,
        )
        self.admin = User.objects.create_user(
            email="admin@ttu.edu.gh",
            password="AdminPass123!",
            username="admin001",
            role=self.admin_role,
        )
        self.client = APIClient()

    @patch("apps.accounts.services.otp_service.OTPDeliveryService.send")
    def test_student_index_skips_password(self, mock_send):
        mock_send.return_value = None
        response = self.client.post(
            "/api/v1/accounts/auth/login/",
            {"identity": "BC/ITS/24/047"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["requires_otp"])
        self.assertIn("otp_request_uuid", data)

    def test_admin_requires_password_before_otp(self):
        response = self.client.post(
            "/api/v1/accounts/auth/login/",
            {"identity": "admin@ttu.edu.gh"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["requires_password"])
        self.assertEqual(data["account_type"], Role.Name.ADMIN)

    @patch("apps.accounts.services.otp_service.OTPDeliveryService.send")
    def test_admin_password_then_otp(self, mock_send):
        mock_send.return_value = None
        gate = self.client.post(
            "/api/v1/accounts/auth/login/",
            {"identity": "admin@ttu.edu.gh"},
            format="json",
        ).json()["data"]
        self.assertTrue(gate["requires_password"])

        response = self.client.post(
            "/api/v1/accounts/auth/login/",
            {"identity": "admin@ttu.edu.gh", "password": "AdminPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data.get("requires_otp"))

    def test_ussd_msisdn_mismatch_rejected(self):
        service = AuthService()
        with self.assertRaises(AuthenticationError) as ctx:
            service.authenticate_student_for_ussd(
                index_number="BC/ITS/24/047",
                msisdn="233209999999",
            )
        self.assertEqual(ctx.exception.code, "msisdn_mismatch")
