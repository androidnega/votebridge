import logging
from datetime import timedelta
from threading import Thread

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
OTP_RESEND_CHAIN_PREFIX = "otp_resend_chain:"


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
        *,
        is_resend: bool = False,
    ) -> OTPRequest:
        max_requests = int(getattr(settings, "OTP_MAX_REQUESTS_PER_WINDOW", 5))
        window_minutes = int(getattr(settings, "OTP_REQUEST_WINDOW_MINUTES", 15))

        if self.otp_repository.count_recent_for_user(user, minutes=window_minutes) >= max_requests:
            raise ValidationError(
                message="Too many OTP requests. Please try again later.",
                code="otp_rate_limited",
            )

        if not is_resend:
            self._reset_resend_chain(user, purpose)

        self.otp_repository.invalidate_active_for_user(user, purpose)

        code = generate_otp_code(length=int(getattr(settings, "OTP_LENGTH", 6)))
        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        max_attempts = int(getattr(settings, "OTP_MAX_ATTEMPTS", 5))

        otp_request = self.otp_repository.create(
            user=user,
            purpose=purpose,
            channel=channel,
            otp_hash=make_password(code),
            expires_at=expires_at,
            max_attempts=max_attempts,
            ip_address=ip_address,
        )

        message = (
            f"Your VoteBridge verification code is {code}. "
            f"It expires in {expiry_minutes} minutes."
        )
        self._dispatch_otp_delivery(
            otp_request=otp_request,
            channel=channel,
            recipient=recipient,
            message=message,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            purpose=purpose,
        )

        return otp_request

    def _dispatch_otp_delivery(
        self,
        *,
        otp_request: OTPRequest,
        channel: str,
        recipient: str,
        message: str,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
        purpose: str,
    ) -> None:
        def deliver() -> None:
            try:
                self.delivery_service.send(
                    channel=channel,
                    recipient=recipient,
                    message=message,
                    user=user,
                )
                logger.info(
                    "OTP sent via %s to %s for user %s",
                    channel,
                    self._mask_recipient_for_log(recipient, channel),
                    user.username,
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
            except Exception:
                logger.exception("OTP delivery failed for user %s", user.username)

        if getattr(settings, "OTP_DELIVERY_ASYNC", True):
            transaction.on_commit(lambda: Thread(target=deliver, daemon=True).start())
            return

        deliver()

    def _resend_chain_key(self, user: User, purpose: str) -> str:
        return f"{OTP_RESEND_CHAIN_PREFIX}{user.id}:{purpose}"

    def _reset_resend_chain(self, user: User, purpose: str) -> None:
        cache.set(
            self._resend_chain_key(user, purpose),
            {"resend_count": 0, "last_sent_at": timezone.now().isoformat()},
            900,
        )

    def enforce_resend_policy(self, user: User, purpose: str) -> None:
        key = self._resend_chain_key(user, purpose)
        meta = cache.get(key) or {"resend_count": 0, "last_sent_at": None}
        max_resends = int(getattr(settings, "OTP_MAX_RESENDS", 3))
        cooldown = int(getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 60))

        if meta.get("resend_count", 0) >= max_resends:
            raise ValidationError(
                message="Maximum OTP resend attempts reached.",
                code="otp_resend_limit",
            )

        last_sent = meta.get("last_sent_at")
        if last_sent:
            last_dt = timezone.datetime.fromisoformat(last_sent)
            if timezone.is_naive(last_dt):
                last_dt = timezone.make_aware(last_dt, timezone.get_current_timezone())
            elapsed = (timezone.now() - last_dt).total_seconds()
            if elapsed < cooldown:
                wait = int(cooldown - elapsed)
                raise ValidationError(
                    message=f"Please wait {wait} seconds before requesting another code.",
                    code="otp_resend_cooldown",
                )

        meta["resend_count"] = meta.get("resend_count", 0) + 1
        meta["last_sent_at"] = timezone.now().isoformat()
        cache.set(key, meta, 900)

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

            if self._dev_otp_fallback_applies(otp_request.user, code):
                return otp_request

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

        if role_name in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            if preferred_channel == OTPRequest.Channel.SMS and user.phone_number:
                return OTPRequest.Channel.SMS, user.phone_number
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

    def _dev_otp_fallback_applies(self, user: User, code: str) -> bool:
        if not getattr(settings, "DEV_OTP_FALLBACK_ENABLED", False):
            return False
        if settings.DEBUG is not True:
            return False

        fallback = str(getattr(settings, "DEV_OTP_FALLBACK_CODE", "") or "").strip()
        allowed = set(getattr(settings, "DEV_OTP_FALLBACK_USERNAMES", []) or [])
        if not fallback or not allowed:
            return False
        if user.username not in allowed and not getattr(user, "demo_seed", False):
            return False
        return str(code or "").strip() == fallback

    @staticmethod
    def _mask_recipient_for_log(recipient: str, channel: str) -> str:
        if channel == OTPRequest.Channel.EMAIL and "@" in recipient:
            local, domain = recipient.split("@", 1)
            masked_local = local[:1] + "***" if local else "***"
            return f"{masked_local}@{domain}"
        digits = "".join(ch for ch in recipient if ch.isdigit())
        if len(digits) >= 4:
            return f"***{digits[-4:]}"
        return "***"
