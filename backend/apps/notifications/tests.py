from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.notifications.models import DeliveryLog, NotificationTemplate
from apps.notifications.providers.base import render_template_text
from apps.notifications.services.communication_service import CommunicationService
from apps.notifications.services.otp_delivery_service import OTPDeliveryService, generate_otp_code

User = get_user_model()


class TemplateRenderingTests(TestCase):
    def test_render_placeholders(self):
        text = "Hello {first_name}, vote in {election_name}."
        result = render_template_text(text, {"first_name": "Kwame", "election_name": "SRC Elections"})
        self.assertEqual(result, "Hello Kwame, vote in SRC Elections.")

    def test_missing_placeholder_preserved(self):
        text = "Hello {first_name}"
        result = render_template_text(text, {})
        self.assertEqual(result, "Hello {first_name}")


class OTPDeliveryTests(TestCase):
    @patch("apps.notifications.services.communication_service.communication_service.send_raw")
    def test_otp_delegates_to_communication_service(self, mock_send_raw):
        service = OTPDeliveryService()
        service.send("sms", "+233241234567", "Your code is 123456")
        mock_send_raw.assert_called_once()
        kwargs = mock_send_raw.call_args.kwargs
        self.assertEqual(kwargs["channel"], "sms")
        self.assertEqual(kwargs["template_code"], "otp_sms")

    def test_generate_otp_code_length(self):
        code = generate_otp_code(6)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class CommunicationServiceTests(TestCase):
    def setUp(self):
        self.service = CommunicationService()
        NotificationTemplate.objects.create(
            code="test_email",
            name="Test",
            channel=NotificationTemplate.Channel.EMAIL,
            subject="Hello {first_name}",
            body_text="Welcome {first_name}",
            body_html="<p>Welcome {first_name}</p>",
            is_active=True,
        )

    def test_dispatch_email_creates_delivery_log(self):
        log = self.service.dispatch(
            template_code="test_email",
            channel=DeliveryLog.Channel.EMAIL,
            recipient="student@ttu.edu.gh",
            context={"first_name": "Ama"},
        )
        self.assertEqual(log.status, DeliveryLog.Status.DELIVERED)
        self.assertIn("Ama", log.body_snapshot)

    def test_dispatch_in_app_requires_user(self):
        user = User.objects.create_user(
            email="kwame@ttu.edu.gh",
            password="testpass123",
            first_name="Kwame",
        )
        NotificationTemplate.objects.create(
            code="test_in_app",
            name="In App",
            channel=NotificationTemplate.Channel.IN_APP,
            in_app_title="Hi {first_name}",
            in_app_body="Message for {first_name}",
            is_active=True,
        )
        log = self.service.dispatch(
            template_code="test_in_app",
            channel=DeliveryLog.Channel.IN_APP,
            recipient=str(user.uuid),
            context={"first_name": "Kwame"},
            user=user,
        )
        self.assertEqual(log.status, DeliveryLog.Status.DELIVERED)
        self.assertEqual(user.in_app_notifications.count(), 1)


class ArkeselProviderTests(TestCase):
    @patch("apps.notifications.providers.base.httpx.post")
    def test_arkesel_send_success(self, mock_post):
        from apps.notifications.providers.base import ArkeselSmsProvider

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b'{"status":"success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        log = DeliveryLog.objects.create(
            recipient="+233241234567",
            channel=DeliveryLog.Channel.SMS,
            body_snapshot="Test SMS",
            status=DeliveryLog.Status.PENDING,
        )

        with override_settings(ARKESEL_API_KEY="test-key", ARKESEL_SENDER_ID="VoteBridge"):
            provider = ArkeselSmsProvider()
            result = provider.send(log)
            self.assertEqual(result["status_code"], mock_response.status_code)
