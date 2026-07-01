import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MFALog, OTPRequest, Role, User
from apps.accounts.repositories.auth_repository import OTPRequestRepository
from apps.accounts.services.mfa_service import MFAService
from apps.notifications.services.otp_delivery_service import OTPDeliveryService, generate_otp_code
from core.exceptions import AuthenticationError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")

OTP_AUTH_RESULT_CACHE_PREFIX = "otp_auth_result:"
OTP_AUTH_RESULT_TTL_SECONDS = 600


class OTPService:
    """OTP generation, delivery, and verification."""

    def __init__(
        self,
        otp_repository: OTPRequestRepository | None = None,
        mfa_service: MFAService | None = None,
        delivery_service: OTPDeliveryService | None = None,
    ):
        self.otp_repository = otp_repository or OTPRequestRepository()
        self.mfa_service = mfa_service or MFAService()
        self.delivery_service = delivery_service or OTPDeliveryService()

    def create_and_send(
        self,
        user: User,
        purpose: str,
        channel: str,
        recipient: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> OTPRequest:
        max_requests = int(getattr(settings, "OTP_MAX_REQUESTS_PER_WINDOW", 5))
        window_minutes = int(getattr(settings, "OTP_REQUEST_WINDOW_MINUTES", 15))

        if self.otp_repository.count_recent_for_user(user, minutes=window_minutes) >= max_requests:
            raise ValidationError(
                message="Too many OTP requests. Please try again later.",
                code="otp_rate_limited",
            )

        self.otp_repository.invalidate_active_for_user(user, purpose)

        code = generate_otp_code(length=int(getattr(settings, "OTP_LENGTH", 6)))
        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 10))
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        otp_request = self.otp_repository.create(
            user=user,
            purpose=purpose,
            channel=channel,
            otp_hash=make_password(code),
            expires_at=expires_at,
            ip_address=ip_address,
        )

        message = (
            f"Your VoteBridge verification code is {code}. "
            f"It expires in {expiry_minutes} minutes."
        )
        self.delivery_service.send(
            channel=channel, recipient=recipient, message=message, user=user
        )

        self.mfa_service.log(
            event_type=MFALog.EventType.OTP_SENT,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "otp_request_uuid": str(otp_request.uuid),
                "channel": channel,
                "purpose": purpose,
            },
        )

        return otp_request

    def get_cached_auth_result(self, otp_request_uuid) -> dict | None:
        return cache.get(f"{OTP_AUTH_RESULT_CACHE_PREFIX}{otp_request_uuid}")

    def cache_auth_result(self, otp_request_uuid, result: dict) -> None:
        cache.set(
            f"{OTP_AUTH_RESULT_CACHE_PREFIX}{otp_request_uuid}",
            result,
            OTP_AUTH_RESULT_TTL_SECONDS,
        )

    def clear_auth_result(self, otp_request_uuid) -> None:
        cache.delete(f"{OTP_AUTH_RESULT_CACHE_PREFIX}{otp_request_uuid}")

    def _get_for_update(self, otp_request_uuid) -> OTPRequest:
        try:
            return (
                OTPRequest.objects.select_for_update()
                .select_related("user", "user__role")
                .get(uuid=otp_request_uuid)
            )
        except OTPRequest.DoesNotExist as exc:
            raise NotFoundError(message="OTP request not found.", code="otp_not_found") from exc

    def validate_code(
        self,
        otp_request_uuid,
        code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> OTPRequest:
        """Validate an OTP code without marking the request as consumed."""
        with transaction.atomic():
            otp_request = self._get_for_update(otp_request_uuid)

            if otp_request.is_verified:
                raise ValidationError(message="OTP has already been used.", code="otp_already_used")

            if timezone.now() > otp_request.expires_at:
                raise ValidationError(message="OTP has expired.", code="otp_expired")

            if otp_request.attempts >= otp_request.max_attempts:
                raise ValidationError(
                    message="Maximum OTP verification attempts exceeded.",
                    code="otp_max_attempts",
                )

            if not check_password(code, otp_request.otp_hash):
                otp_request.attempts += 1
                otp_request.save(update_fields=["attempts"])
                self.mfa_service.log(
                    event_type=MFALog.EventType.OTP_FAILED,
                    user=otp_request.user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata={"otp_request_uuid": str(otp_request.uuid)},
                )
                raise AuthenticationError(message="Invalid OTP code.", code="invalid_otp")

        return otp_request

    def mark_consumed(
        self,
        otp_request: OTPRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        with transaction.atomic():
            locked = self._get_for_update(otp_request.uuid)
            if locked.is_verified:
                return

            locked.is_verified = True
            locked.verified_at = timezone.now()
            locked.save(update_fields=["is_verified", "verified_at"])

            self.mfa_service.log(
                event_type=MFALog.EventType.OTP_VERIFIED,
                user=locked.user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"otp_request_uuid": str(locked.uuid)},
            )

    def verify(
        self,
        otp_request_uuid,
        code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> OTPRequest:
        otp_request = self.validate_code(
            otp_request_uuid=otp_request_uuid,
            code=code,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.mark_consumed(otp_request, ip_address=ip_address, user_agent=user_agent)
        return otp_request

    def resolve_channel_and_recipient(self, user: User, preferred_channel: str | None = None):
        role_name = user.role.name

        if role_name in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            if user.phone_number:
                return OTPRequest.Channel.SMS, user.phone_number
            if user.email:
                return OTPRequest.Channel.EMAIL, user.email
            raise ValidationError(
                message="No phone number or email available for OTP delivery.",
                code="otp_recipient_missing",
            )

        if preferred_channel == OTPRequest.Channel.SMS and user.phone_number:
            return OTPRequest.Channel.SMS, user.phone_number

        if user.email:
            return OTPRequest.Channel.EMAIL, user.email

        raise ValidationError(
            message="No email available for OTP delivery.",
            code="otp_recipient_missing",
        )
