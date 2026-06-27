"""USSD flow tests and provider simulation."""

from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase, override_settings

from apps.ussd.models import USSDRequestLog, USSDSession
from apps.ussd.services.ussd_controller_service import UssdControllerService
from apps.ussd.services.ussd_flow_service import UssdFlowService, UssdResponse


class UssdControllerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.controller = UssdControllerService(flow_service=MagicMock())

    def test_form_callback_parses_session(self):
        request = self.factory.post(
            "/api/v1/ussd/callback/",
            {
                "sessionId": "sess-123",
                "phoneNumber": "+233241234567",
                "text": "",
                "serviceCode": "*928*1#",
            },
        )
        self.controller.flow_service.handle_request.return_value = UssdResponse(
            "CON Welcome", True
        )
        content_type, body, _ = self.controller.handle_callback(request)
        self.assertEqual(content_type, "text/plain")
        self.assertIn("CON", body)
        self.controller.flow_service.handle_request.assert_called_once()

    def test_json_callback_format(self):
        import json

        payload = {
            "sessionID": "json-sess-1",
            "msisdn": "233241234567",
            "newSession": True,
            "userData": "*928*1#",
            "network": "MTN",
        }
        request = self.factory.post(
            "/api/v1/ussd/callback/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.controller.flow_service.handle_request.return_value = UssdResponse(
            "Welcome", True
        )
        content_type, body, _ = self.controller.handle_callback(request)
        self.assertEqual(content_type, "application/json")
        parsed = json.loads(body)
        self.assertTrue(parsed["continueSession"])


class UssdFlowSessionTests(TestCase):
    @override_settings(
        USSD_SESSION_TIMEOUT_MINUTES=5,
        USSD_RATE_LIMIT_PER_MSISDN=100,
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    )
    def test_welcome_shows_main_menu(self):
        service = UssdFlowService()
        response = service.handle_request(
            session_id="test-session-1",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        self.assertTrue(response.continue_session)
        self.assertIn("Vote", response.message)
        session = USSDSession.objects.get(session_id="test-session-1")
        self.assertEqual(session.current_step, "MAIN_MENU")
        self.assertEqual(USSDRequestLog.objects.filter(carrier_session_id="test-session-1").count(), 1)

    @override_settings(USSD_SESSION_TIMEOUT_MINUTES=5, USSD_RATE_LIMIT_PER_MSISDN=100)
    def test_exit_ends_session(self):
        service = UssdFlowService()
        service.handle_request(
            session_id="test-exit",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        response = service.handle_request(
            session_id="test-exit",
            msisdn="233241234567",
            inputs=["6"],
        )
        self.assertFalse(response.continue_session)
        self.assertIn("END", response.message)


class UssdAuthIntegrationTests(TestCase):
    @override_settings(
        USSD_SESSION_TIMEOUT_MINUTES=5,
        USSD_RATE_LIMIT_PER_MSISDN=100,
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    )
    @patch("apps.ussd.services.ussd_flow_service.AuthService.authenticate_student_for_ussd")
    def test_auth_flow_prompts_index_then_pin(self, mock_auth):
        from apps.accounts.models import Role, User

        user = MagicMock()
        user.uuid = "00000000-0000-0000-0000-000000000001"
        mock_auth.return_value = user

        service = UssdFlowService()
        service.handle_request(
            session_id="auth-flow",
            msisdn="233241234567",
            inputs=[],
            is_new_session=True,
        )
        service.handle_request(session_id="auth-flow", msisdn="233241234567", inputs=["1"])
        r_index = service.handle_request(
            session_id="auth-flow", msisdn="233241234567", inputs=["BC/ITS/24/047"]
        )
        self.assertIn("PIN", r_index.message)
        service.handle_request(session_id="auth-flow", msisdn="233241234567", inputs=["1234"])
        mock_auth.assert_called_once()
