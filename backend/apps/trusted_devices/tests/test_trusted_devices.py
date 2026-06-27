from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import Role, Session, User
from apps.system.models import FeatureFlag, SystemSetting
from apps.trusted_devices.constants import (
    DeviceType,
    RISK_ALLOW,
    RISK_REQUIRE_BIOMETRIC,
    TrustLevel,
)
from apps.trusted_devices.models import TrustedDeviceLoginHistory
from apps.trusted_devices.services.impossible_travel_service import impossible_travel_service
from apps.trusted_devices.services.registration_service import trusted_device_registration_service
from apps.trusted_devices.services.risk_assessment_service import risk_assessment_service
from apps.trusted_devices.services.risk_score_service import device_risk_score_service
from apps.trusted_devices.services.trust_level_service import device_trust_level_service
from apps.trusted_devices.services.trusted_device_service import trusted_device_service
from apps.trusted_devices.utils import build_device_context, generate_device_token, hash_device_token


@override_settings(BIOMETRICS_INFERENCE_MODE="mock")
class TrustedDeviceRiskTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(name=Role.Name.ADMIN, defaults={"description": "Admin"})
        self.super_role, _ = Role.objects.get_or_create(name=Role.Name.SUPER_ADMIN, defaults={"description": "SA"})
        self.student_role, _ = Role.objects.get_or_create(name=Role.Name.STUDENT, defaults={"description": "Student"})

        self.super_admin = User.objects.create_user(
            email="td-sa@test.local",
            username="td-sa",
            password="TestPass123!",
            role=self.super_role,
        )
        self.admin = User.objects.create_user(
            email="td-admin@test.local",
            username="td-admin",
            password="TestPass123!",
            role=self.admin_role,
        )
        self.student = User.objects.create_user(
            email="td-student@test.local",
            username="td-student",
            password="TestPass123!",
            role=self.student_role,
        )

        FeatureFlag.objects.update_or_create(
            key="future_biometrics",
            defaults={"label": "Biometrics", "description": "", "enabled": True},
        )
        for key, val in (
            ("identity_assurance.enable_trusted_devices", True),
            ("identity_assurance.enable_risk_based_authentication", True),
            ("identity_assurance.enable_active_liveness", False),
            ("identity_assurance.enable_device_trust_levels", True),
            ("identity_assurance.enable_impossible_travel_detection", True),
            ("identity_assurance.enable_device_expiration", True),
            ("identity_assurance.enable_device_risk_scores", True),
            ("identity_assurance.enable_university_device_policies", True),
        ):
            SystemSetting.objects.update_or_create(
                key=key,
                defaults={"category": "identity_assurance", "value": {"value": val}, "description": ""},
            )

    def test_student_always_allowed(self):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="student-fp")
        decision = risk_assessment_service.assess_login(
            self.student,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            context=context,
        )
        self.assertEqual(decision.action, RISK_ALLOW)

    def test_new_device_requires_biometric(self):
        context = build_device_context(user_agent="Mozilla/5.0 Chrome", browser_fingerprint="new-device-fp")
        decision = risk_assessment_service.assess_login(
            self.admin,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 Chrome",
            context=context,
            trusted_device_token=None,
        )
        self.assertEqual(decision.action, RISK_REQUIRE_BIOMETRIC)

    def test_trusted_device_allows_login(self):
        context = build_device_context(user_agent="Mozilla/5.0 Chrome", browser_fingerprint="trusted-fp-1")
        raw_token, device = trusted_device_registration_service.register_after_biometric(
            self.admin,
            context,
            ip_address="127.0.0.1",
        )
        self.assertTrue(raw_token)
        self.assertIsNotNone(device)
        self.assertEqual(device.trust_level, TrustLevel.HIGH)

        decision = risk_assessment_service.assess_login(
            self.admin,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 Chrome",
            context=context,
            trusted_device_token=raw_token,
        )
        self.assertEqual(decision.action, RISK_ALLOW)
        self.assertIsNotNone(decision.trusted_device)

    def test_invalid_token_requires_biometric(self):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="fp-x")
        decision = risk_assessment_service.assess_login(
            self.admin,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            context=context,
            trusted_device_token="invalid-token-value",
        )
        self.assertEqual(decision.action, RISK_REQUIRE_BIOMETRIC)

    def test_token_hash_is_stable(self):
        token = generate_device_token()
        h1 = hash_device_token(token, str(self.admin.uuid))
        h2 = hash_device_token(token, str(self.admin.uuid))
        self.assertEqual(h1, h2)

    def test_trust_level_medium_without_recent_biometric(self):
        context = build_device_context(user_agent="Mozilla/5.0 Chrome", browser_fingerprint="trust-fp-2")
        _, device = trusted_device_registration_service.register_after_biometric(
            self.admin, context, ip_address="127.0.0.1"
        )
        device.last_biometric = timezone.now() - timedelta(hours=48)
        device.risk_score = 10.0
        device.save(update_fields=["last_biometric", "risk_score"])
        level = device_trust_level_service.compute_trust_level(device)
        self.assertEqual(level, TrustLevel.MEDIUM)

    def test_expired_device_requires_biometric(self):
        context = build_device_context(user_agent="Mozilla/5.0 Chrome", browser_fingerprint="expired-fp")
        raw_token, device = trusted_device_registration_service.register_after_biometric(
            self.admin, context, ip_address="127.0.0.1"
        )
        device.expires_at = timezone.now() - timedelta(days=1)
        device.save(update_fields=["expires_at"])

        decision = risk_assessment_service.assess_login(
            self.admin,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 Chrome",
            context=context,
            trusted_device_token=raw_token,
        )
        self.assertEqual(decision.action, RISK_REQUIRE_BIOMETRIC)
        self.assertIn("expired_trust", decision.reasons)

    def test_impossible_travel_requires_biometric(self):
        now = timezone.now()
        TrustedDeviceLoginHistory.objects.create(
            user=self.admin,
            device=trusted_device_registration_service.register_after_biometric(
                self.admin,
                build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="travel-fp"),
                ip_address="127.0.0.1",
            )[1],
            logged_in_at=now - timedelta(minutes=30),
            country="Ghana",
            city="Takoradi",
            browser_name="Chrome",
            operating_system="Windows",
            authentication_method="trusted_device",
            risk_score=5.0,
            ip_address="127.0.0.1",
        )

        result = impossible_travel_service.check(
            self.admin,
            country="Germany",
            city="Berlin",
            login_time=now,
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.decision, RISK_REQUIRE_BIOMETRIC)

    @patch("apps.trusted_devices.services.notification_service.communication_service.send_raw")
    def test_device_registered_notification(self, mock_send):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="notify-fp")
        trusted_device_registration_service.register_after_biometric(self.admin, context, ip_address="127.0.0.1")
        self.assertTrue(mock_send.called)

    def test_risk_score_decreases_on_biometric_success(self):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="risk-fp")
        _, device = trusted_device_registration_service.register_after_biometric(
            self.admin, context, ip_address="127.0.0.1"
        )
        device.risk_score = 60.0
        device.save(update_fields=["risk_score"])
        device_risk_score_service.record_biometric_success(device)
        device.refresh_from_db()
        self.assertLess(device.risk_score, 60.0)

    def test_university_device_policy(self):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="uni-fp")
        _, device = trusted_device_registration_service.register_after_biometric(
            self.admin, context, ip_address="127.0.0.1", device_type=DeviceType.UNIVERSITY_MANAGED
        )
        assigned = trusted_device_service.assign_university_managed(self.super_admin, device.uuid)
        self.assertEqual(assigned.device_type, DeviceType.UNIVERSITY_MANAGED)
        self.assertGreater(assigned.expires_at, timezone.now() + timedelta(days=30))

    def test_revoke_terminates_sessions(self):
        context = build_device_context(user_agent="Mozilla/5.0", browser_fingerprint="revoke-fp")
        _, device = trusted_device_registration_service.register_after_biometric(
            self.admin, context, ip_address="127.0.0.1"
        )
        Session.objects.create(
            user=self.admin,
            refresh_token_jti="test-jti-revoke",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            expires_at=timezone.now() + timedelta(days=7),
            last_activity_at=timezone.now(),
        )
        trusted_device_service.revoke_device(self.admin, device.uuid)
        device.refresh_from_db()
        self.assertTrue(device.is_revoked)
        self.assertEqual(device.trust_level, TrustLevel.REVOKED)
        self.assertFalse(Session.objects.filter(user=self.admin, is_active=True).exists())
