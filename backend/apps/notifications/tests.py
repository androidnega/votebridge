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

    def test_arkesel_uses_encrypted_config_api_key(self):
        from apps.notifications.models import CommunicationProvider
        from apps.notifications.providers.base import ArkeselSmsProvider
        from apps.system.utils import encrypt_secret

        record = CommunicationProvider.objects.create(
            name="Arkesel Encrypted",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={
                "api_key": encrypt_secret("stored-key"),
                "sender_id": "VoteBridge",
            },
        )

        provider = ArkeselSmsProvider(record)
        api_key, sender_id, _url = provider._credentials()
        self.assertEqual(api_key, "stored-key")
        self.assertEqual(sender_id, "VoteBridge")


class MoolreProviderTests(TestCase):
    @patch("apps.notifications.providers.base.httpx.post")
    def test_moolre_send_success(self, mock_post):
        from apps.notifications.providers.base import MoolreSmsProvider

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status":1}'
        mock_response.json.return_value = {"status": 1}
        mock_post.return_value = mock_response

        log = DeliveryLog.objects.create(
            recipient="0241234567",
            channel=DeliveryLog.Channel.SMS,
            body_snapshot="Test SMS",
            status=DeliveryLog.Status.PENDING,
        )

        with override_settings(MOOLRE_VAS_KEY="vas-key", MOOLRE_SENDER_ID="VoteBridge"):
            provider = MoolreSmsProvider()
            result = provider.send(log)
            self.assertEqual(result["provider"], "moolre_sms")
            payload = mock_post.call_args.kwargs["json"]
            self.assertEqual(payload["messages"][0]["recipient"], "233241234567")

    @patch("apps.notifications.providers.base.httpx.post")
    def test_sms_fallback_to_moolre_when_arkesel_fails(self, mock_post):
        import httpx
        from apps.notifications.models import CommunicationProvider

        NotificationTemplate.objects.get_or_create(
            code="otp_sms_fallback",
            defaults={
                "name": "OTP SMS",
                "channel": NotificationTemplate.Channel.SMS,
                "sms_body": "Code {otp_code}",
                "is_active": True,
            },
        )

        CommunicationProvider.objects.create(
            name="Arkesel Primary",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={"api_key": "test", "sender_id": "VoteBridge"},
        )
        CommunicationProvider.objects.create(
            name="Moolre Fallback",
            provider_type=CommunicationProvider.ProviderType.MOOLRE_SMS,
            is_active=True,
            is_default=False,
            config={"vas_key": "vas-key", "sender_id": "VoteBridge"},
        )

        calls = {"count": 0}

        def side_effect(*args, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise httpx.ConnectError("Arkesel timeout", request=MagicMock())
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"status":1}'
            mock_response.json.return_value = {"status": 1}
            return mock_response

        mock_post.side_effect = side_effect

        service = CommunicationService()
        with override_settings(
            ARKESEL_API_KEY="test-key",
            ARKESEL_SENDER_ID="VoteBridge",
            MOOLRE_VAS_KEY="vas-key",
            MOOLRE_SENDER_ID="VoteBridge",
        ):
            log = service.send_raw(
                channel="sms",
                recipient="233241234567",
                body="Code 123456",
                template_code="otp_sms_fallback",
            )

        self.assertEqual(log.status, DeliveryLog.Status.DELIVERED)
        self.assertTrue(log.provider_response.get("fallback_used"))
        self.assertEqual(mock_post.call_count, 2)


class SmsProductionReadinessTests(TestCase):
    @patch("apps.notifications.providers.base.httpx.post")
    def test_otp_sms_delivery_via_communication_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status":"success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        NotificationTemplate.objects.get_or_create(
            code="otp_sms",
            defaults={
                "name": "OTP SMS",
                "channel": NotificationTemplate.Channel.SMS,
                "sms_body": "Your VoteBridge code is {otp_code}",
                "is_active": True,
            },
        )
        from apps.notifications.models import CommunicationProvider

        CommunicationProvider.objects.create(
            name="Arkesel Test",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={"api_key": "test", "sender_id": "VoteBridge"},
        )

        service = CommunicationService()
        with override_settings(ARKESEL_API_KEY="test-key", ARKESEL_SENDER_ID="VoteBridge"):
            log = service.send_raw(
                channel="sms",
                recipient="233241234567",
                body="Your VoteBridge code is 123456",
                template_code="otp_sms",
            )
        self.assertEqual(log.status, DeliveryLog.Status.DELIVERED)

    @patch("apps.notifications.providers.base.httpx.post")
    def test_vote_confirmation_template_dispatch(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status":"success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        NotificationTemplate.objects.get_or_create(
            code="vote_confirmation",
            defaults={
                "name": "Vote Confirmation",
                "channel": NotificationTemplate.Channel.SMS,
                "sms_body": "Your vote in {election_name} was recorded. Token: {token_code}",
                "is_active": True,
            },
        )
        from apps.notifications.models import CommunicationProvider

        CommunicationProvider.objects.create(
            name="Arkesel Vote",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={"api_key": "test", "sender_id": "VoteBridge"},
        )

        service = CommunicationService()
        with override_settings(ARKESEL_API_KEY="test-key", ARKESEL_SENDER_ID="VoteBridge"):
            log = service.dispatch(
                template_code="vote_confirmation",
                channel=DeliveryLog.Channel.SMS,
                recipient="233241234567",
                context={"election_name": "SRC 2026", "token_code": "SVT-ABC"},
            )
        self.assertEqual(log.status, DeliveryLog.Status.DELIVERED)
        self.assertIn("SRC 2026", log.body_snapshot)

    @patch("apps.notifications.providers.base.httpx.post")
    def test_sms_delivery_failure_sets_retry_status(self, mock_post):
        mock_post.side_effect = Exception("Arkesel timeout")

        NotificationTemplate.objects.get_or_create(
            code="otp_sms_retry",
            defaults={
                "name": "OTP",
                "channel": NotificationTemplate.Channel.SMS,
                "sms_body": "Code {otp_code}",
                "is_active": True,
            },
        )
        from apps.notifications.models import CommunicationProvider

        CommunicationProvider.objects.create(
            name="Arkesel Fail",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={"api_key": "test", "sender_id": "VoteBridge"},
        )

        service = CommunicationService()
        with override_settings(ARKESEL_API_KEY="test-key", ARKESEL_SENDER_ID="VoteBridge"):
            with self.assertRaises(Exception):
                service.send_raw(
                    channel="sms",
                    recipient="233241234567",
                    body="Code 999999",
                    template_code="otp_sms_retry",
                )

        log = DeliveryLog.objects.order_by("-created_at").first()
        self.assertEqual(log.status, DeliveryLog.Status.RETRYING)
        self.assertEqual(log.retry_count, 1)

    @patch("apps.notifications.providers.base.httpx.post")
    def test_retry_delivery_succeeds_after_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status":"success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        from apps.notifications.models import CommunicationProvider

        CommunicationProvider.objects.create(
            name="Arkesel Retry",
            provider_type=CommunicationProvider.ProviderType.ARKESEL_SMS,
            is_active=True,
            is_default=True,
            config={"api_key": "test", "sender_id": "VoteBridge"},
        )

        log = DeliveryLog.objects.create(
            recipient="233241234567",
            channel=DeliveryLog.Channel.SMS,
            body_snapshot="Retry me",
            status=DeliveryLog.Status.RETRYING,
            retry_count=1,
            max_retries=3,
        )
        service = CommunicationService()
        with override_settings(ARKESEL_API_KEY="test-key", ARKESEL_SENDER_ID="VoteBridge"):
            updated = service.retry_delivery(log)
        self.assertEqual(updated.status, DeliveryLog.Status.DELIVERED)
