import logging

from apps.notifications.services.communication_service import communication_service

logger = logging.getLogger("votebridge")


class OTPDeliveryService:
    """Delivers OTP codes via Communication Service — all sends flow through central hub."""

    def send(self, channel: str, recipient: str, message: str, user=None) -> None:
        template_code = "otp_sms" if channel == "sms" else "otp_email"
        communication_service.send_raw(
            channel=channel,
            recipient=recipient,
            body=message,
            subject="VoteBridge Verification Code" if channel == "email" else "",
            user=user,
            template_code=template_code,
            metadata={"purpose": "otp"},
        )


def generate_otp_code(length: int = 6) -> str:
    import secrets

    return "".join(str(secrets.randbelow(10)) for _ in range(length))
