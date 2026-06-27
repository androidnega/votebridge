import base64
import hashlib

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.biometrics.models import BiometricProfile, BiometricVerificationLog
from apps.biometrics.services.enrollment_service import biometric_enrollment_service
from apps.biometrics.services.policy_service import biometric_policy_service
from apps.biometrics.services.verification_service import biometric_verification_service
from apps.system.models import FeatureFlag


def _mock_image(seed: str) -> str:
    raw = hashlib.sha256(seed.encode()).digest()
    return base64.b64encode(raw).decode()


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class BiometricPolicyTests(TestCase):
    def setUp(self):
        self.super_role, _ = Role.objects.get_or_create(name=Role.Name.SUPER_ADMIN, defaults={"description": "SA"})
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT, defaults={"description": "Student"})
        self.super_admin = User.objects.create_user(
            email="bio-sa@test.local",
            username="bio-sa",
            password="TestPass123!",
            role=self.super_role,
        )
        self.admin = User.objects.create_user(
            email="bio-admin@test.local",
            username="bio-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.student = User.objects.create_user(
            email="bio-student@test.local",
            username="bio-student",
            password="TestPass123!",
            role=self.student_role,
        )
        flag, _ = FeatureFlag.objects.get_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": True},
        )
        flag.enabled = True
        flag.save()

    def test_student_not_required_for_biometrics(self):
        self.assertFalse(biometric_policy_service.requires_verification_at_login(self.student))

    def test_admin_required_when_enrolled(self):
        images = [_mock_image(f"enroll-{i}") for i in range(10)]
        biometric_enrollment_service.enroll(
            actor=self.super_admin,
            target_user=self.admin,
            images=images,
        )
        self.assertTrue(biometric_policy_service.requires_verification_at_login(self.admin))


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class BiometricEnrollmentTests(TestCase):
    def setUp(self):
        self.super_role, _ = Role.objects.get_or_create(name=Role.Name.SUPER_ADMIN, defaults={"description": "SA"})
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.super_admin = User.objects.create_user(
            email="bio-enroll-sa@test.local",
            username="bio-enroll-sa",
            password="TestPass123!",
            role=self.super_role,
        )
        self.admin = User.objects.create_user(
            email="bio-enroll-admin@test.local",
            username="bio-enroll-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        FeatureFlag.objects.update_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": True},
        )

    def test_enrollment_creates_profile(self):
        images = [_mock_image(f"img-{i}") for i in range(10)]
        result = biometric_enrollment_service.enroll(
            actor=self.super_admin,
            target_user=self.admin,
            images=images,
        )
        self.assertTrue(BiometricProfile.objects.filter(user=self.admin).exists())
        self.assertEqual(result["enrollment_images_count"], 10)

    def test_admin_cannot_enroll(self):
        images = [_mock_image(f"img-{i}") for i in range(10)]
        with self.assertRaises(Exception):
            biometric_enrollment_service.enroll(
                actor=self.admin,
                target_user=self.super_admin,
                images=images,
            )


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class BiometricVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_role, _ = Role.objects.get_or_create(name=Role.Name.SUPER_ADMIN, defaults={"description": "SA"})
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.admin = User.objects.create_user(
            email="bio-verify-admin@test.local",
            username="bio-verify-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.super_admin = User.objects.create_user(
            email="bio-verify-sa@test.local",
            username="bio-verify-sa",
            password="TestPass123!",
            role=self.super_role,
        )
        FeatureFlag.objects.update_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": True},
        )
        from apps.system.models import SystemSetting

        for key, val in (
            ("identity_assurance.enable_active_liveness", False),
            ("identity_assurance.enable_passive_liveness", True),
        ):
            SystemSetting.objects.update_or_create(
                key=key,
                defaults={
                    "category": "identity_assurance",
                    "value": {"value": val},
                    "description": "",
                    "is_sensitive": False,
                    "is_public": False,
                },
            )
        images = [_mock_image(f"enroll-{i}") for i in range(10)]
        biometric_enrollment_service.enroll(
            actor=self.super_admin,
            target_user=self.admin,
            images=images,
        )

    def test_status_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("biometrics:status"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["data"]["enrolled"])

    def test_verify_login_with_matching_frames(self):
        pending = biometric_verification_service.create_pending_auth(self.admin, "otp-uuid")
        frames = [_mock_image(f"enroll-{i}") for i in range(3)]
        result = biometric_verification_service.verify_login(
            pending_auth_token=pending["pending_auth_token"],
            challenge_id=pending["challenge"]["challenge_id"],
            frames=frames,
        )
        self.assertIn("tokens", result)
        self.assertTrue(result["verification"]["matched"])

    def test_verify_login_fails_with_wrong_image(self):
        pending = biometric_verification_service.create_pending_auth(self.admin, "otp-uuid-2")
        frames = [_mock_image("completely-different-face")]
        with self.assertRaises(Exception):
            biometric_verification_service.verify_login(
                pending_auth_token=pending["pending_auth_token"],
                challenge_id=pending["challenge"]["challenge_id"],
                frames=frames,
            )
        self.assertTrue(
            BiometricVerificationLog.objects.filter(
                user=self.admin,
                event_type=BiometricVerificationLog.EventType.VERIFICATION_FAILED,
            ).exists()
        )
