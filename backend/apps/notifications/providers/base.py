import logging
import re
from abc import ABC, abstractmethod

import httpx
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from apps.notifications.models import CommunicationProvider, DeliveryLog
from core.exceptions import ServiceUnavailableError

logger = logging.getLogger("votebridge")

PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")


class BaseProvider(ABC):
    provider_type: str = ""

    @abstractmethod
    def send(self, delivery_log: DeliveryLog) -> dict:
        """Send message and return provider response dict."""

    @abstractmethod
    def test_connection(self) -> dict:
        """Test provider connectivity."""


class ArkeselSmsProvider(BaseProvider):
    provider_type = CommunicationProvider.ProviderType.ARKESEL_SMS

    def __init__(self, provider_record: CommunicationProvider | None = None):
        self.provider_record = provider_record

    def _credentials(self) -> tuple[str, str, str]:
        config = (self.provider_record.config if self.provider_record else {}) or {}
        api_key = config.get("api_key") or getattr(settings, "ARKESEL_API_KEY", "")
        sender_id = config.get("sender_id") or getattr(settings, "ARKESEL_SENDER_ID", "")
        url = config.get("url") or getattr(
            settings,
            "ARKESEL_SMS_URL",
            "https://sms.arkesel.com/api/v2/sms/send",
        )
        return api_key, sender_id, url

    def send(self, delivery_log: DeliveryLog) -> dict:
        api_key, sender_id, url = self._credentials()
        if not api_key or not sender_id:
            raise ServiceUnavailableError(
                message="SMS delivery is not configured.",
                code="sms_not_configured",
            )

        try:
            response = httpx.post(
                url,
                headers={"api-key": api_key},
                json={
                    "sender": sender_id,
                    "message": delivery_log.body_snapshot,
                    "recipients": [delivery_log.recipient],
                },
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            return {"status_code": response.status_code, "response": data}
        except httpx.HTTPError as exc:
            logger.error("Arkesel SMS delivery failed: %s", exc)
            raise ServiceUnavailableError(
                message="Failed to send SMS.",
                code="sms_delivery_failed",
            ) from exc

    def test_connection(self) -> dict:
        api_key, sender_id, _url = self._credentials()
        if not api_key or not sender_id:
            return {"success": False, "message": "Arkesel API key or sender ID not configured."}
        return {"success": True, "message": "Arkesel credentials are configured."}


class SmtpEmailProvider(BaseProvider):
    provider_type = CommunicationProvider.ProviderType.SMTP_EMAIL

    def __init__(self, provider_record: CommunicationProvider | None = None):
        self.provider_record = provider_record

    def send(self, delivery_log: DeliveryLog) -> dict:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@votebridge.local")
        if self.provider_record and self.provider_record.config.get("from_email"):
            from_email = self.provider_record.config["from_email"]

        subject = delivery_log.subject or "VoteBridge Notification"
        body_text = delivery_log.body_snapshot
        body_html = delivery_log.metadata.get("body_html", "")

        try:
            if body_html:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=body_text,
                    from_email=from_email,
                    to=[delivery_log.recipient],
                )
                email.attach_alternative(body_html, "text/html")
                email.send(fail_silently=False)
            else:
                from django.core.mail import send_mail

                send_mail(
                    subject=subject,
                    message=body_text,
                    from_email=from_email,
                    recipient_list=[delivery_log.recipient],
                    fail_silently=False,
                )

            return {"delivered": True, "recipient": delivery_log.recipient}
        except Exception as exc:
            logger.error("Email delivery failed: %s", exc)
            raise ServiceUnavailableError(
                message="Failed to send email.",
                code="email_delivery_failed",
            ) from exc

    def test_connection(self) -> dict:
        backend = getattr(settings, "EMAIL_BACKEND", "")
        if "console" in backend:
            return {"success": True, "message": f"Email backend: {backend} (development)."}
        host = getattr(settings, "EMAIL_HOST", "")
        if not host:
            return {"success": False, "message": "SMTP host not configured."}
        return {"success": True, "message": f"SMTP configured: {host}"}


PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    CommunicationProvider.ProviderType.ARKESEL_SMS: ArkeselSmsProvider,
    CommunicationProvider.ProviderType.SMTP_EMAIL: SmtpEmailProvider,
}


def get_provider_instance(provider_record: CommunicationProvider | None, provider_type: str) -> BaseProvider:
    cls = PROVIDER_REGISTRY.get(provider_type)
    if not cls:
        raise ServiceUnavailableError(
            message=f"Unknown provider type: {provider_type}",
            code="unknown_provider",
        )
    return cls(provider_record)


def render_template_text(text: str, context: dict) -> str:
    if not text:
        return ""

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return str(context.get(key, match.group(0)))

    return PLACEHOLDER_PATTERN.sub(replacer, text)
