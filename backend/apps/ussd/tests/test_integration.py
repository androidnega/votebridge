"""USSD integration configuration and audit tests."""

import json
from unittest.mock import patch
from urllib.parse import urlencode

from django.test import RequestFactory, TestCase, override_settings
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.ussd.models import USSDRequestLog
from apps.ussd.services.ussd_audit_service import UssdAuditService
from apps.ussd.services.ussd_config_service import UssdConfigService
from apps.ussd.services.ussd_controller_service import UssdControllerService
from apps.ussd.services.ussd_flow_service import UssdResponse
from core.public_urls import build_public_url


@override_settings(PUBLIC_BASE_URL="https://votebridge.example.edu")
class UssdConfigServiceTests(TestCase):
    def test_callback_url_uses_public_base_url(self):
        service = UssdConfigService()
        self.assertEqual(
            service.get_callback_url(),
            "https://votebridge.example.edu/api/v1/ussd/callback/",
        )
        self.assertEqual(
            build_public_url("/api/v1/ussd/callback/"),
            "https://votebridge.example.edu/api/v1/ussd/callback/",
        )

    def test_integration_config_includes_environment_and_health(self):
        service = UssdConfigService()
        config = service.get_integration_config()
        self.assertEqual(config["callback_url"], "https://votebridge.example.edu/api/v1/ussd/callback/")
        self.assertIn(config["environment"], {"development", "production"})
        self.assertIn(config["health_status"], {"unconfigured", "pending", "healthy", "degraded"})
        self.assertIn("reachable", config["health"])


class UssdAuditServiceTests(TestCase):
    def test_record_callback_enriches_existing_log(self):
        log = USSDRequestLog.objects.create(
            carrier_session_id="audit-sess-1",
            msisdn="233241234567",
            duration_ms=120,
        )
        service = UssdAuditService()
        service.record_callback(
            session_id="audit-sess-1",
            msisdn="233241234567",
            provider_user_id="VOTEBRIDGE",
            request_payload={"raw": {"sessionID": "audit-sess-1"}},
            response_payload={"sessionID": "audit-sess-1", "continueSession": True},
            http_status=200,
            duration_ms=180,
            ip_address="127.0.0.1",
        )
        log.refresh_from_db()
        self.assertEqual(log.provider_user_id, "VOTEBRIDGE")
        self.assertEqual(log.http_status, 200)
        self.assertEqual(log.duration_ms, 180)
        self.assertEqual(log.request_payload["raw"]["sessionID"], "audit-sess-1")
        self.assertTrue(log.response_payload["continueSession"])


class UssdResponseValidationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.controller = UssdControllerService(flow_service=__import__("unittest").mock.MagicMock())

    def test_invalid_response_is_replaced_with_system_error(self):
        request = self.factory.post(
            "/api/v1/ussd/callback/",
            data=json.dumps(
                {
                    "sessionID": "validate-sess",
                    "msisdn": "233241234567",
                    "newSession": True,
                    "userData": "*928*1#",
                }
            ),
            content_type="application/json",
        )
        self.controller.flow_service.handle_request.return_value = UssdResponse("CON Welcome", True)

        with patch.object(self.controller, "_validate_arkesel_response", return_value=False):
            _content_type, body, parsed, _audit = self.controller.handle_callback(request)

        self.assertFalse(parsed["continueSession"])
        self.assertIn("System error", parsed["message"])
        self.assertIn("System error", json.loads(body)["message"])


@override_settings(PUBLIC_BASE_URL="https://votebridge.example.edu", ARKESEL_USSD_CALLBACK_SECRET="")
class UssdIntegrationApiTests(APITestCase):
    def setUp(self):
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN,
            defaults={"description": "Super Admin"},
        )
        self.super_admin = User.objects.create_user(
            email="sa-ussd@test.local",
            username="sa-ussd",
            password="TestPass123!",
            first_name="SA",
            last_name="USSD",
            role=self.super_role,
        )

    def test_integration_endpoint_returns_configuration(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/v1/ussd/integration/")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["callback_url"], "https://votebridge.example.edu/api/v1/ussd/callback/")
        self.assertEqual(data["health"]["callback_url"], data["callback_url"])


@override_settings(ARKESEL_USSD_CALLBACK_SECRET="")
class UssdCallbackAuditIntegrationTests(APITestCase):
    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_callback_records_audit_payload(self, mock_handle):
        mock_handle.return_value = UssdResponse("CON Welcome", True)
        payload = {
            "sessionID": "audit-api-sess",
            "userID": "ARKESEL",
            "newSession": True,
            "msisdn": "233241234567",
            "userData": "*928*1#",
        }
        response = self.client.post(
            "/api/v1/ussd/callback/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        log = USSDRequestLog.objects.filter(carrier_session_id="audit-api-sess").order_by("-created_at").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.http_status, 200)
        self.assertEqual(log.provider_user_id, "ARKESEL")
        self.assertIn("raw", log.request_payload)
        self.assertEqual(log.response_payload["sessionID"], "audit-api-sess")
        self.assertTrue(log.response_payload["continueSession"])

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_form_callback_records_audit_payload(self, mock_handle):
        mock_handle.return_value = UssdResponse("END Goodbye", False)
        response = self.client.post(
            "/api/v1/ussd/callback/",
            data=urlencode(
                {
                    "sessionId": "audit-form-sess",
                    "phoneNumber": "233271231234",
                    "text": "0",
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        log = USSDRequestLog.objects.filter(carrier_session_id="audit-form-sess").order_by("-created_at").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.response_payload["continueSession"], False)


class UssdCallbackDebugLoggingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(DEBUG=True)
    @patch("apps.ussd.services.ussd_callback_debug.logger")
    def test_log_incoming_callback_in_development(self, mock_logger):
        from apps.ussd.services.ussd_callback_debug import log_incoming_callback

        request = self.factory.post(
            "/api/v1/ussd/callback/",
            data=json.dumps(
                {
                    "sessionID": "debug-sess",
                    "userID": "ARKESEL",
                    "newSession": True,
                    "msisdn": "233241234567",
                    "userData": "*928*1#",
                }
            ),
            content_type="application/json",
            HTTP_X_ARKESEL_SECRET="super-secret",
        )
        log_incoming_callback(request)

        mock_logger.info.assert_called_once()
        prefix = mock_logger.info.call_args[0][1]
        details = mock_logger.info.call_args[0][2]
        self.assertEqual(prefix, "[USSD CALLBACK DEBUG]")
        self.assertIn("POST", details)
        self.assertIn("application/json", details)
        self.assertIn("233241234567", details)
        self.assertIn("[REDACTED]", details)
        self.assertNotIn("super-secret", details)

    @override_settings(DEBUG=False)
    @patch("apps.ussd.services.ussd_callback_debug.logger")
    def test_log_incoming_callback_disabled_when_not_debug(self, mock_logger):
        from apps.ussd.services.ussd_callback_debug import log_incoming_callback

        request = self.factory.post(
            "/api/v1/ussd/callback/",
            data=json.dumps({"sessionID": "debug-sess-off", "msisdn": "233241234567"}),
            content_type="application/json",
        )
        log_incoming_callback(request)
        mock_logger.info.assert_not_called()
