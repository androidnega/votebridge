import logging
import secrets
import uuid

from django.conf import settings
from django.core.cache import cache

from apps.accounts.models import OTPRequest, User
from apps.accounts.services.otp_service import OTPService
from apps.system.constants import STEP_UP_CACHE_PREFIX, STEP_UP_TTL_SECONDS
from core.exceptions import AuthenticationError, ValidationError

logger = logging.getLogger("votebridge")


class StepUpAuthService:
    """Session elevation via OTP for sensitive SCC actions."""

    def __init__(self, otp_service: OTPService | None = None):
        self.otp_service = otp_service or OTPService()

    def request_challenge(self, user: User, *, ip_address: str | None = None, user_agent: str | None = None) -> dict:
        channel = OTPRequest.Channel.EMAIL if user.email else OTPRequest.Channel.SMS
        recipient = user.email or user.phone_number
        if not recipient:
            raise ValidationError(message="No contact method available for step-up OTP.", code="no_contact")

        otp_request = self.otp_service.create_and_send(
            user=user,
            purpose=OTPRequest.Purpose.MFA,
            channel=channel,
            recipient=recipient,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return {
            "challenge_id": str(otp_request.uuid),
            "channel": channel,
            "expires_in_minutes": int(getattr(settings, "OTP_EXPIRY_MINUTES", 10)),
        }

    def verify_challenge(
        self,
        user: User,
        *,
        challenge_id: str,
        code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        otp_request = self.otp_service.verify(
            otp_request_uuid=challenge_id,
            code=code,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        if otp_request.user_id != user.id:
            raise AuthenticationError(message="Invalid step-up challenge.", code="invalid_challenge")

        token = secrets.token_urlsafe(32)
        cache_key = f"{STEP_UP_CACHE_PREFIX}{user.uuid}:{token}"
        cache.set(cache_key, str(user.uuid), STEP_UP_TTL_SECONDS)
        return {
            "step_up_token": token,
            "expires_in_seconds": STEP_UP_TTL_SECONDS,
        }

    def validate_token(self, user: User, token: str) -> None:
        cache_key = f"{STEP_UP_CACHE_PREFIX}{user.uuid}:{token}"
        stored = cache.get(cache_key)
        if not stored or str(stored) != str(user.uuid):
            raise ValidationError(
                message="Step-up authentication is required or has expired.",
                code="step_up_required",
            )

    def consume_token(self, user: User, token: str) -> None:
        self.validate_token(user, token)
        cache.delete(f"{STEP_UP_CACHE_PREFIX}{user.uuid}:{token}")


step_up_auth_service = StepUpAuthService()
