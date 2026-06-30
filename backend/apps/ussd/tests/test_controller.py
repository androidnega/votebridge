"""USSD flow tests and provider simulation."""

from unittest.mock import MagicMock

from django.test import RequestFactory, TestCase

from apps.ussd.services.ussd_controller_service import UssdControllerService
from apps.ussd.services.ussd_flow_service import UssdResponse


class UssdControllerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.controller = UssdControllerService(flow_service=MagicMock())

    def test_form_callback_parses_session(self):
        import json

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
        content_type, body, parsed, _audit = self.controller.handle_callback(request)
        self.assertEqual(content_type, "application/json")
        response = json.loads(body)
        self.assertEqual(response["sessionID"], "sess-123")
        self.assertEqual(response["msisdn"], "233241234567")
        self.assertEqual(response["message"], "Welcome")
        self.assertTrue(response["continueSession"])
        self.assertEqual(parsed, response)
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
        content_type, body, parsed, _audit = self.controller.handle_callback(request)
        self.assertEqual(content_type, "application/json")
        response = json.loads(body)
        self.assertEqual(response["sessionID"], "json-sess-1")
        self.assertEqual(response["userID"], "VOTEBRIDGE")
        self.assertEqual(response["msisdn"], "233241234567")
        self.assertEqual(response["message"], "Welcome")
        self.assertTrue(response["continueSession"])
