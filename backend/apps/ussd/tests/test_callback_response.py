"""Integration tests for Arkesel USSD callback response format."""

import json
from unittest.mock import patch
from urllib.parse import urlencode

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.ussd.services.ussd_flow_service import UssdResponse

ARKESEL_RESPONSE_KEYS = frozenset(
    {"sessionID", "userID", "msisdn", "message", "continueSession"}
)

CALLBACK_URL = "/api/v1/ussd/callback/"


@override_settings(
    ARKESEL_USSD_CALLBACK_SECRET="",
    ARKESEL_USSD_USER_ID="VOTEBRIDGE_TEST",
)
class UssdCallbackResponseIntegrationTests(APITestCase):
    def _assert_arkesel_response(self, response, *, session_id, msisdn, continue_session):
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response["Content-Type"].startswith("application/json"),
            msg=f"Unexpected Content-Type: {response['Content-Type']}",
        )

        body = json.loads(response.content.decode("utf-8"))
        self.assertEqual(set(body.keys()), ARKESEL_RESPONSE_KEYS)
        self.assertNotIn("success", body)
        self.assertNotIn("data", body)

        self.assertEqual(body["sessionID"], session_id)
        self.assertEqual(body["userID"], "VOTEBRIDGE_TEST")
        self.assertEqual(body["msisdn"], msisdn)
        self.assertIsInstance(body["message"], str)
        self.assertIsInstance(body["continueSession"], bool)
        self.assertEqual(body["continueSession"], continue_session)
        self.assertNotIn("CON ", body["message"])
        self.assertNotIn("END ", body["message"])

        return body

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_new_session_json_request_returns_arkesel_json(self, mock_handle):
        mock_handle.return_value = UssdResponse("CON Welcome to VoteBridge", True)

        payload = {
            "sessionID": "ark-sess-new",
            "userID": "ARKESEL",
            "newSession": True,
            "msisdn": "233241234567",
            "userData": "*928*1#",
            "network": "MTN",
        }
        response = self.client.post(
            CALLBACK_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )

        body = self._assert_arkesel_response(
            response,
            session_id="ark-sess-new",
            msisdn="233241234567",
            continue_session=True,
        )
        self.assertIn("Welcome", body["message"])

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_continuing_session_json_request_returns_same_schema(self, mock_handle):
        mock_handle.return_value = UssdResponse("CON Enter your PIN:", True)

        payload = {
            "sessionID": "ark-sess-cont",
            "userID": "ARKESEL",
            "newSession": False,
            "msisdn": "233271231234",
            "userData": "1",
            "network": "AIRTELTIGO",
        }
        response = self.client.post(
            CALLBACK_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self._assert_arkesel_response(
            response,
            session_id="ark-sess-cont",
            msisdn="233271231234",
            continue_session=True,
        )

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_terminated_session_json_request_sets_continue_session_false(self, mock_handle):
        mock_handle.return_value = UssdResponse("END Thank you for using VoteBridge.", False)

        payload = {
            "sessionID": "ark-sess-end",
            "newSession": False,
            "msisdn": "233241234567",
            "userData": "6",
            "network": "MTN",
        }
        response = self.client.post(
            CALLBACK_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )

        body = self._assert_arkesel_response(
            response,
            session_id="ark-sess-end",
            msisdn="233241234567",
            continue_session=False,
        )
        self.assertIn("Thank you", body["message"])

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_form_encoded_request_returns_arkesel_json(self, mock_handle):
        mock_handle.return_value = UssdResponse("CON Welcome to VoteBridge", True)

        response = self.client.post(
            CALLBACK_URL,
            data=urlencode(
                {
                    "sessionId": "form-sess-1",
                    "phoneNumber": "+233241234567",
                    "text": "",
                    "serviceCode": "*928*1#",
                    "type": "initiation",
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )

        self._assert_arkesel_response(
            response,
            session_id="form-sess-1",
            msisdn="233241234567",
            continue_session=True,
        )

    @patch("apps.ussd.services.ussd_flow_service.ussd_flow_service.handle_request")
    def test_form_encoded_continuing_request_returns_arkesel_json(self, mock_handle):
        mock_handle.return_value = UssdResponse("END Invalid index number or PIN.", False)

        response = self.client.post(
            CALLBACK_URL,
            data=urlencode(
                {
                    "sessionId": "form-sess-2",
                    "phoneNumber": "233271231234",
                    "text": "1*wrong-pin",
                    "serviceCode": "*928*1#",
                    "type": "response",
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )

        self._assert_arkesel_response(
            response,
            session_id="form-sess-2",
            msisdn="233271231234",
            continue_session=False,
        )
