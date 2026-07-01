import logging
import re
from abc import ABC, abstractmethod

import httpx
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from apps.notifications.models import CommunicationProvider, DeliveryLog
from apps.system.utils import decrypt_secret
from core.exceptions import ServiceUnavailableError

logger = logging.getLogger("votebridge")

PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")


def resolve_config_secret(value: str | None) -> str:
    """Return a config secret, decrypting stored values when signed."""
    if not value:
        return ""
    try:
        return decrypt_secret(value)
    except ValueError:
        return value


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
        api_key = resolve_config_secret(config.get("api_key")) or getattr(settings, "ARKESEL_API_KEY", "")
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


class MoolreSmsProvider(BaseProvider):
    """Moolre SMS gateway — fallback when Arkesel delivery fails."""

    provider_type = CommunicationProvider.ProviderType.MOOLRE_SMS

    LIVE_URL = "https://api.moolre.com/open/sms/send"
    SANDBOX_URL = "https://sandbox.moolre.com/open/sms/send"
    STATUS_URL = "https://api.moolre.com/open/sms/query"

    def __init__(self, provider_record: CommunicationProvider | None = None):
        self.provider_record = provider_record

    def _credentials(self) -> tuple[str, str, str]:
        config = (self.provider_record.config if self.provider_record else {}) or {}
        vas_key = resolve_config_secret(config.get("vas_key")) or getattr(settings, "MOOLRE_VAS_KEY", "")
        sender_id = config.get("sender_id") or getattr(settings, "MOOLRE_SENDER_ID", "")
        environment = (config.get("environment") or getattr(settings, "MOOLRE_ENVIRONMENT", "live")).lower()
        url = config.get("url") or (
            self.SANDBOX_URL if environment == "sandbox" else self.LIVE_URL
        )
        return vas_key, sender_id, url

    def _normalize_recipient(self, recipient: str) -> str:
        digits = re.sub(r"\D", "", recipient or "")
        if digits.startswith("0") and len(digits) == 10:
            return f"233{digits[1:]}"
        return digits

    def send(self, delivery_log: DeliveryLog) -> dict:
        vas_key, sender_id, url = self._credentials()
        if not vas_key or not sender_id:
            raise ServiceUnavailableError(
                message="Moolre SMS is not configured.",
                code="sms_not_configured",
            )

        recipient = self._normalize_recipient(delivery_log.recipient)
        payload = {
            "type": 1,
            "senderid": sender_id[:11],
            "messages": [
                {
                    "recipient": recipient,
                    "message": delivery_log.body_snapshot[:160],
                    "ref": str(delivery_log.uuid),
                }
            ],
        }

        try:
            response = httpx.post(
                url,
                headers={"X-API-VASKEY": vas_key, "Content-Type": "application/json"},
                json=payload,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            if data.get("status") not in (1, "1", True):
                raise ServiceUnavailableError(
                    message=data.get("message") or "Moolre SMS delivery failed.",
                    code="sms_delivery_failed",
                )
            return {"status_code": response.status_code, "response": data, "provider": "moolre_sms"}
        except httpx.HTTPError as exc:
            logger.error("Moolre SMS delivery failed: %s", exc)
            raise ServiceUnavailableError(
                message="Failed to send SMS via Moolre.",
                code="sms_delivery_failed",
            ) from exc

    def test_connection(self) -> dict:
        vas_key, sender_id, _url = self._credentials()
        if not vas_key:
            return {"success": False, "message": "Moolre VAS key not configured."}
        if not sender_id:
            return {"success": False, "message": "Moolre sender ID not configured."}

        environment = (
            (self.provider_record.config or {}).get("environment")
            if self.provider_record
            else getattr(settings, "MOOLRE_ENVIRONMENT", "live")
        )
        status_url = (
            "https://sandbox.moolre.com/open/sms/query"
            if str(environment).lower() == "sandbox"
            else self.STATUS_URL
        )

        try:
            response = httpx.post(
                status_url,
                headers={"X-API-VASKEY": vas_key, "Content-Type": "application/json"},
                json={"type": 2},
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            if data.get("status") in (1, "1", True):
                balance = (data.get("data") or {}).get("balance")
                msg = "Moolre credentials verified."
                if balance is not None:
                    msg = f"Moolre connected. SMS balance: {balance}."
                return {"success": True, "message": msg}
            return {
                "success": False,
                "message": data.get("message") or "Moolre authentication failed.",
            }
        except httpx.HTTPError as exc:
            logger.error("Moolre SMS test failed: %s", exc)
            return {"success": False, "message": "Could not reach Moolre SMS API."}


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
    CommunicationProvider.ProviderType.MOOLRE_SMS: MoolreSmsProvider,
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
