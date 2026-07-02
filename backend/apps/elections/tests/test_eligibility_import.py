"""Tests for voter eligibility CSV/Excel import."""

import io
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.elections.models import Election, VoterEligibility
from apps.elections.services.eligibility_import_service import parse_eligibility_upload


class EligibilityImportParserTests(TestCase):
    def test_parse_csv_with_headers(self):
        content = (
            "index_number,email,is_eligible,eligibility_reason\n"
            "BC/ITS/24/001,,yes,Registered student voter\n"
            ",student@example.com,no,Programme exclusion\n"
        ).encode()
        upload = SimpleUploadedFile("voters.csv", content, content_type="text/csv")
        rows, errors = parse_eligibility_upload(upload)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["index_number"], "BC/ITS/24/001")
        self.assertTrue(rows[0]["is_eligible"])
        self.assertFalse(rows[1]["is_eligible"])

    def test_parse_single_column_without_headers(self):
        content = b"BC/ITS/24/002\nBC/ITS/24/003\n"
        upload = SimpleUploadedFile("voters.csv", content, content_type="text/csv")
        rows, errors = parse_eligibility_upload(upload)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["index_number"], "BC/ITS/24/002")


class EligibilityImportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT, defaults={"description": "Student"})
        self.admin = User.objects.create_user(
            email="import-admin@test.local",
            username="import-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.student = User.objects.create_user(
            email="import-student@test.local",
            username="import-student",
            password="1234",
            index_number="BC/ITS/24/047",
            role=self.student_role,
        )
        self.unknown_student = User.objects.create_user(
            email="import-other@test.local",
            username="import-other",
            password="1234",
            index_number="BC/ITS/24/099",
            role=self.student_role,
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Import Test Election",
            election_type=Election.ElectionType.STUDENT_UNION,
            start_date=now,
            end_date=now + timedelta(days=1),
            status=Election.Status.DRAFT,
            allow_web_voting=True,
            created_by=self.admin,
        )
        self.url = reverse(
            "elections:election-eligibility-import",
            kwargs={"election_uuid": self.election.uuid},
        )

    def _csv_upload(self, content: str, **extra):
        data = {
            "file": SimpleUploadedFile("voters.csv", content.encode(), content_type="text/csv"),
            **extra,
        }
        return data

    def test_import_creates_eligibility_records(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.url,
            self._csv_upload(
                "index_number\n"
                "BC/ITS/24/047\n"
                "BC/ITS/24/999\n"
            ),
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data["data"]
        self.assertEqual(payload["imported"], 1)
        self.assertEqual(payload["not_found_count"], 1)
        self.assertIn("BC/ITS/24/999", payload["not_found"])
        self.assertTrue(
            VoterEligibility.objects.filter(election=self.election, user=self.student).exists()
        )

    def test_import_updates_existing_record(self):
        VoterEligibility.objects.create(
            election=self.election,
            user=self.student,
            is_eligible=False,
            eligibility_reason="Old reason",
        )
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.url,
            self._csv_upload(
                "index_number,is_eligible,eligibility_reason\n"
                "BC/ITS/24/047,yes,Updated via import\n"
            ),
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["updated"], 1)
        record = VoterEligibility.objects.get(election=self.election, user=self.student)
        self.assertTrue(record.is_eligible)
        self.assertEqual(record.eligibility_reason, "Updated via import")

    def test_import_rejects_unsupported_file_type(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.url,
            {
                "file": SimpleUploadedFile("voters.txt", b"BC/ITS/24/047", content_type="text/plain"),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_xlsx(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            self.skipTest("openpyxl not installed")

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["index_number", "eligibility_reason"])
        sheet.append(["BC/ITS/24/047", "Excel import"])
        sheet.append(["BC/ITS/24/099", "Excel import"])
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.url,
            {
                "file": SimpleUploadedFile(
                    "voters.xlsx",
                    buffer.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["processed"], 2)


class EligibilityCreateByIndexTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT, defaults={"description": "Student"})
        self.admin = User.objects.create_user(
            email="eligibility-admin@test.local",
            username="eligibility-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.student = User.objects.create_user(
            email="eligibility-student@test.local",
            username="eligibility-student",
            password="1234",
            index_number="BC/ITS/24/047",
            role=self.student_role,
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Eligibility Create Test",
            election_type=Election.ElectionType.STUDENT_UNION,
            start_date=now,
            end_date=now + timedelta(days=1),
            status=Election.Status.DRAFT,
            allow_web_voting=True,
            created_by=self.admin,
        )
        self.url = reverse(
            "elections:election-eligibility-list",
            kwargs={"election_uuid": self.election.uuid},
        )

    def test_create_by_index_number_updates_phone(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.url,
            {
                "index_number": "bc/its/24/047",
                "phone_number": "0247940801",
                "is_eligible": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.student.refresh_from_db()
        self.assertEqual(self.student.phone_number, "233247940801")
        self.assertEqual(response.data["data"]["user_phone_number"], "233247940801")
        self.assertTrue(
            VoterEligibility.objects.filter(election=self.election, user=self.student).exists()
        )
