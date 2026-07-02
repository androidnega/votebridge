from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role, User
from apps.accounts.services import user_service
from core.exceptions import ValidationError


class RolePermissionBoundaryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_role, _ = Role.objects.get_or_create(
            name=Role.Name.STUDENT,
            defaults={"description": "Student"},
        )
        self.candidate_role, _ = Role.objects.get_or_create(
            name=Role.Name.CANDIDATE,
            defaults={"description": "Candidate"},
        )
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.super_admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )

        self.student = User.objects.create_user(
            email="student-perm@test.local",
            password="TestPass123!",
            index_number="BC/ITS/24/900",
            role=self.student_role,
        )
        self.admin = User.objects.create_user(
            email="admin-perm@test.local",
            username="admin-perm",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.super_admin = User.objects.create_user(
            email="super-perm@test.local",
            username="super-perm",
            password="TestPass123!",
            role=self.super_admin_role,
        )
        self.users_url = reverse("accounts:user-list")

    def test_student_self_profile_cannot_change_index_number(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(
            "/api/v1/accounts/auth/me/",
            {"index_number": "BC/ITS/24/999"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.index_number, "BC/ITS/24/900")

    def test_student_self_profile_can_update_contact_fields(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(
            "/api/v1/accounts/auth/me/",
            {"first_name": "Updated", "phone_number": "233241111111"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Updated")
        self.assertEqual(self.student.phone_number, "233241111111")

    def test_update_self_profile_service_rejects_institutional_fields(self):
        with self.assertRaises(ValidationError):
            user_service.update_self_profile(self.student, {"index_number": "BC/ITS/24/888"})

    def test_admin_can_lookup_students_but_not_create_users(self):
        self.client.force_authenticate(user=self.admin)
        list_response = self.client.get(self.users_url, {"role": "student"})
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        create_response = self.client.post(
            self.users_url,
            {
                "email": "new-student@test.local",
                "password": "TestPass123!",
                "first_name": "New",
                "last_name": "Student",
                "role_name": "student",
                "index_number": "BC/ITS/24/901",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_lookup_super_admin_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url, {"role": "super_admin"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_create_users(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            self.users_url,
            {
                "email": "created-by-sa@test.local",
                "password": "TestPass123!",
                "first_name": "Created",
                "last_name": "User",
                "role_name": "student",
                "index_number": "BC/ITS/24/902",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
