from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import OTPRequest, Role, User
from apps.accounts.repositories.auth_repository import OTPRequestRepository
from apps.accounts.services import auth_service
from apps.biometrics.services.policy_service import biometric_policy_service
from apps.system.models import FeatureFlag


def _mock_image_seed(seed: str) -> str:
    import base64
    import hashlib

    return base64.b64encode(hashlib.sha256(seed.encode()).digest()).decode()


@override_settings(BIOMETRIC_AUTH_ENABLED=False, BIOMETRICS_INFERENCE_MODE="mock")
class LoginBiometricPolicyDisabledTests(TestCase):
    """Phase 48 — mandatory biometric auth off for v1.0."""

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(
            name=Role.Name.STUDENT, defaults={"description": "Student"}
        )
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN, defaults={"description": "Admin"}
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN, defaults={"description": "Super Admin"}
        )
        FeatureFlag.objects.update_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": True},
        )
        self.student = User.objects.create_user(
            email="phase48-student@test.local",
            username="phase48-student",
            password="TestPass123!",
            role=self.student_role,
            index_number="BC/ITS/24/001",
            phone_number="+233200000001",
        )
        self.admin = User.objects.create_user(
            email="phase48-admin@test.local",
            username="phase48-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.super_admin = User.objects.create_user(
            email="phase48-sa@test.local",
            username="phase48-sa",
            password="TestPass123!",
            role=self.super_role,
        )

    def _create_otp(self, user, code="123456"):
        return OTPRequestRepository().create(
            user=user,
            purpose=OTPRequest.Purpose.LOGIN,
            channel=OTPRequest.Channel.EMAIL,
            otp_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def _verify(self, user, code="123456"):
        otp = self._create_otp(user, code)
        return auth_service.verify_otp_and_authenticate(
            otp_request_uuid=str(otp.uuid),
            otp_code=code,
        )

    def test_policy_disabled_for_all_roles(self):
        self.assertFalse(biometric_policy_service.is_auth_enabled())
        self.assertFalse(biometric_policy_service.is_module_enabled())
        self.assertFalse(biometric_policy_service.requires_verification_at_login(self.student))
        self.assertFalse(biometric_policy_service.requires_verification_at_login(self.admin))
        self.assertFalse(biometric_policy_service.requires_verification_at_login(self.super_admin))

    def test_student_otp_returns_tokens_not_biometric(self):
        result = self._verify(self.student)
        self.assertIn("tokens", result)
        self.assertNotIn("requires_biometric", result)
        self.assertNotIn("requires_enrollment", result)
        self.assertEqual(result["redirect_path"], "/dashboard/student")

    def test_admin_otp_returns_tokens_not_biometric(self):
        result = self._verify(self.admin)
        self.assertIn("tokens", result)
        self.assertNotIn("requires_biometric", result)
        self.assertNotIn("requires_enrollment", result)
        self.assertEqual(result["redirect_path"], "/dashboard/admin")

    def test_super_admin_otp_returns_tokens_not_biometric(self):
        result = self._verify(self.super_admin)
        self.assertIn("tokens", result)
        self.assertNotIn("requires_biometric", result)
        self.assertNotIn("requires_enrollment", result)
        self.assertEqual(result["redirect_path"], "/dashboard/super-admin")

    def test_enrolled_admin_still_skips_biometric_when_disabled(self):
        from apps.biometrics.models import BiometricProfile

        BiometricProfile.objects.create(
            user=self.admin,
            is_active=True,
            quality_score=0.9,
            encrypted_embedding="dGVzdA==",
            enrollment_images_count=10,
        )
        result = self._verify(self.admin)
        self.assertIn("tokens", result)
        self.assertNotIn("requires_biometric", result)


@override_settings(BIOMETRIC_AUTH_ENABLED=True, BIOMETRICS_INFERENCE_MODE="mock")
class LoginBiometricPolicyEnabledTests(TestCase):
    """Ensure future activation path still works when explicitly enabled."""

    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN, defaults={"description": "Admin"}
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN, defaults={"description": "Super Admin"}
        )
        FeatureFlag.objects.update_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "Biometrics", "enabled": True},
        )
        self.super_admin = User.objects.create_user(
            email="phase48-enabled-sa@test.local",
            username="phase48-enabled-sa",
            password="TestPass123!",
            role=self.super_role,
        )
        self.admin = User.objects.create_user(
            email="phase48-enabled-admin@test.local",
            username="phase48-enabled-admin",
            password="TestPass123!",
            role=self.admin_role,
        )

    def _create_otp(self, user, code="123456"):
        return OTPRequestRepository().create(
            user=user,
            purpose=OTPRequest.Purpose.LOGIN,
            channel=OTPRequest.Channel.EMAIL,
            otp_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def test_admin_without_profile_requires_enrollment(self):
        otp = self._create_otp(self.admin)
        result = auth_service.verify_otp_and_authenticate(
            otp_request_uuid=str(otp.uuid),
            otp_code="123456",
        )
        self.assertTrue(result.get("requires_enrollment"))
        self.assertIn("pending_auth_token", result)
