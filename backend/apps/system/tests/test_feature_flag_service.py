"""Phase 49 — centralized feature flag enforcement."""

import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase, override_settings

from apps.notifications.models import DeliveryLog
from apps.notifications.services.communication_service import CommunicationService
from apps.accounts.models import Role, User
from apps.system.models import FeatureFlag
from apps.system.services.feature_flag_service import feature_flag_service
from apps.system.services.system_service import SystemSettingsService
from apps.ussd.services.ussd_controller_service import UssdControllerService
from core.exceptions import ValidationError


class FeatureFlagServiceTests(TestCase):
    def test_ensure_defaults_creates_new_flags(self):
        FeatureFlag.objects.filter(key="email_notifications").delete()
        feature_flag_service.ensure_defaults()
        self.assertTrue(FeatureFlag.objects.filter(key="email_notifications").exists())

    def test_is_channel_enabled_respects_sms_flag(self):
        flag, _ = FeatureFlag.objects.update_or_create(
            key="sms",
            defaults={"name": "SMS", "description": "SMS", "enabled": False},
        )
        feature_flag_service._invalidate_cache("sms")
        self.assertFalse(feature_flag_service.is_sms_enabled())
        flag.enabled = True
        flag.save()
        feature_flag_service._invalidate_cache("sms")
        self.assertTrue(feature_flag_service.is_sms_enabled())

    def test_settings_api_filters_flag_managed_keys(self):
        service = SystemSettingsService()
        keys = {item["key"] for item in service.get_category("ussd")}
        self.assertNotIn("ussd.voting_enabled", keys)

    def test_settings_update_rejects_flag_managed_key(self):
        role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        user = User.objects.create_user(
            email="flag-admin@test.edu",
            username="flag-admin",
            password="testpass123",
            role=role,
        )
        service = SystemSettingsService()
        with patch(
            "apps.system.services.system_service.step_up_auth_service.validate_token",
            return_value=None,
        ):
            with self.assertRaises(ValidationError) as ctx:
                service.update_settings(
                    user,
                    "ussd",
                    {"voting_enabled": False},
                    step_up_token="tok",
                )
        self.assertEqual(ctx.exception.code, "flag_managed_setting")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class UssdDisabledControllerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.controller = UssdControllerService(flow_service=MagicMock())

    def test_disabled_ussd_terminates_without_flow(self):
        FeatureFlag.objects.update_or_create(
            key="ussd",
            defaults={"name": "USSD", "description": "USSD", "enabled": False},
        )
        feature_flag_service._invalidate_cache("ussd")

        request = self.factory.post(
            "/api/v1/ussd/callback/",
            data=json.dumps(
                {
                    "sessionID": "disabled-sess",
                    "msisdn": "233241234567",
                    "newSession": True,
                    "userData": "*928*1#",
                }
            ),
            content_type="application/json",
        )
        content_type, body, parsed, _audit = self.controller.handle_callback(request)
        self.assertEqual(content_type, "application/json")
        response = json.loads(body)
        self.assertFalse(response["continueSession"])
        self.assertIn("USSD voting is currently unavailable", response["message"])
        self.controller.flow_service.handle_request.assert_not_called()

        FeatureFlag.objects.update_or_create(
            key="ussd",
            defaults={"name": "USSD", "description": "USSD", "enabled": True},
        )
        feature_flag_service._invalidate_cache("ussd")


class SmsDisabledCommunicationTests(TestCase):
    def test_send_raw_raises_when_sms_disabled(self):
        FeatureFlag.objects.update_or_create(
            key="sms",
            defaults={"name": "SMS", "description": "SMS", "enabled": False},
        )
        feature_flag_service._invalidate_cache("sms")

        service = CommunicationService()
        with self.assertRaises(ValidationError) as ctx:
            service.send_raw(
                channel=DeliveryLog.Channel.SMS,
                recipient="+233241234567",
                body="Test",
            )
        self.assertEqual(ctx.exception.code, "channel_disabled")

        FeatureFlag.objects.update_or_create(
            key="sms",
            defaults={"name": "SMS", "description": "SMS", "enabled": True},
        )
        feature_flag_service._invalidate_cache("sms")
