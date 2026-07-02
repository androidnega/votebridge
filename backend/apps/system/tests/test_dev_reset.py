"""Development reset and bootstrap tests."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import OTPRequest, Role
from apps.accounts.services.otp_service import OTPService
from apps.elections.models import Election
from apps.notifications.models import CommunicationProvider
from apps.system.models import SystemSetting
from apps.system.services.dev_reset_service import dev_reset_service
from core.exceptions import AuthenticationError, ValidationError

User = get_user_model()


@override_settings(DEBUG=True)
class DevResetServiceTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        self.demo_student = User.objects.create_user(
            email="student-demo@test.edu",
            password="demo",
            username="student-demo",
            role=self.admin_role,
        )
        now = timezone.now()
        Election.objects.create(
            title="Demo Election",
            created_by=self.demo_student,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status=Election.Status.DRAFT,
        )
        SystemSetting.objects.get_or_create(
            key="public_base_url",
            defaults={"category": "integrations", "value": {"url": "https://example.test"}},
        )

    def test_reset_clears_users_and_elections_and_bootstraps_accounts(self):
        summary = dev_reset_service.reset_and_bootstrap()

        self.assertEqual(Election.objects.count(), 0)
        self.assertFalse(User.objects.filter(username="student-demo").exists())
        self.assertTrue(User.objects.filter(username="superadmin").exists())
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertEqual(SystemSetting.objects.filter(key="public_base_url").count(), 1)
        self.assertGreaterEqual(summary.cleared["users"], 1)

    def test_reset_preserves_communication_providers(self):
        before = CommunicationProvider.objects.count()
        CommunicationProvider.objects.create(
            name="Dev SMS",
            provider_type="arkesel_sms",
            is_active=True,
            config={"api_key": "test"},
        )
        dev_reset_service.reset_and_bootstrap()
        self.assertEqual(CommunicationProvider.objects.count(), before + 1)

    @override_settings(DEBUG=False)
    def test_reset_blocked_outside_debug(self):
        with self.assertRaises(ValidationError):
            dev_reset_service.reset_and_bootstrap()


@override_settings(
    DEBUG=True,
    DEV_OTP_FALLBACK_ENABLED=True,
    DEV_OTP_FALLBACK_CODE="111111",
    DEV_OTP_FALLBACK_USERNAMES=["superadmin"],
)
class DevOtpFallbackTests(TestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        self.user = User.objects.create_user(
            email="superadmin@votebridge.local",
            password="[REDACTED]",
            username="superadmin",
            role=role,
            phone_number="233257940791",
        )
        self.service = OTPService()

    def test_fallback_accepts_expired_otp_for_bootstrap_user(self):
        otp_request = OTPRequest.objects.create(
            user=self.user,
            purpose=OTPRequest.Purpose.LOGIN,
            channel=OTPRequest.Channel.SMS,
            otp_hash="unused",
            expires_at=timezone.now() - timedelta(minutes=5),
            max_attempts=5,
        )
        validated = self.service.validate_code(otp_request.uuid, "111111")
        self.assertEqual(validated.uuid, otp_request.uuid)

    @override_settings(DEBUG=False)
    def test_fallback_disabled_outside_debug(self):
        otp_request = OTPRequest.objects.create(
            user=self.user,
            purpose=OTPRequest.Purpose.LOGIN,
            channel=OTPRequest.Channel.SMS,
            otp_hash="unused",
            expires_at=timezone.now() + timedelta(minutes=5),
            max_attempts=5,
        )
        with self.assertRaises(AuthenticationError):
            self.service.validate_code(otp_request.uuid, "111111")

    def test_admin_prefers_sms_when_phone_present(self):
        admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN,
            defaults={"description": "Admin"},
        )
        admin = User.objects.create_user(
            email="admin@votebridge.local",
            password="[REDACTED]",
            username="admin",
            role=admin_role,
            phone_number="233257940792",
        )
        channel, recipient = self.service.resolve_channel_and_recipient(admin)
        self.assertEqual(channel, OTPRequest.Channel.SMS)
        self.assertEqual(recipient, "233257940792")
