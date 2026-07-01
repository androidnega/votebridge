import logging

from apps.accounts.models import MFALog, OTPRequest, Role, User
from apps.accounts.repositories.user_repository import UserRepository
from apps.accounts.services.mfa_service import MFAService
from apps.accounts.services.otp_service import OTPService
from apps.accounts.services.session_service import SessionService
from apps.system.services.feature_flag_service import feature_flag_service
from core.exceptions import AuthenticationError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

INVALID_CREDENTIALS_MESSAGE = "Invalid credentials."

DASHBOARD_ROUTES = {
    Role.Name.STUDENT: "/dashboard/student",
    Role.Name.CANDIDATE: "/dashboard/student",
    Role.Name.ADMIN: "/dashboard/admin",
    Role.Name.SUPER_ADMIN: "/dashboard/super-admin",
}


class AuthService:
    """Authentication flows for students, admins, and super admins."""

    STUDENT_ROLES = {Role.Name.STUDENT, Role.Name.CANDIDATE}
    ADMIN_ROLES = {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}

    def __init__(
        self,
        user_repository: UserRepository | None = None,
        otp_service: OTPService | None = None,
        session_service: SessionService | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.user_repository = user_repository or UserRepository()
        self.otp_service = otp_service or OTPService()
        self.session_service = session_service or SessionService()
        self.mfa_service = mfa_service or MFAService()

    def login(
        self,
        identity: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        """Universal identity login — resolves index, username, or email server-side."""
        user = self._resolve_user_by_identity(identity)

        if not user or not user.check_password(password):
            self._log_failed_login(identity, ip_address, user_agent, user)
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        return self._initiate_login_for_user(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def _resolve_user_by_identity(self, identity: str) -> User | None:
        raw = (identity or "").strip()
        if not raw:
            return None

        if "@" in raw:
            return self.user_repository.get_by_email(raw)

        if "/" in raw:
            return self.user_repository.get_by_index_number(raw)

        user = self.user_repository.get_by_username(raw)
        if user:
            return user

        return self.user_repository.get_by_index_number(raw)

    def _initiate_login_for_user(
        self,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        role_name = user.role.name

        if role_name == Role.Name.SUPER_ADMIN:
            self.mfa_service.log(
                event_type=MFALog.EventType.MFA_REQUIRED,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"flow": "universal_login"},
            )
            if not feature_flag_service.is_otp_enabled():
                return self._complete_password_login(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    mfa_completed=True,
                )
            return self._initiate_otp_login(
                user=user,
                purpose=OTPRequest.Purpose.MFA,
                ip_address=ip_address,
                user_agent=user_agent,
                mfa_required=True,
            )

        if not feature_flag_service.is_otp_enabled():
            return self._complete_password_login(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return self._initiate_otp_login(
            user=user,
            purpose=OTPRequest.Purpose.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def _log_failed_login(
        self,
        identity: str,
        ip_address: str | None,
        user_agent: str | None,
        user: User | None = None,
    ) -> None:
        self.mfa_service.log(
            event_type=MFALog.EventType.LOGIN_FAILED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"flow": "universal_login"},
        )

    def dashboard_path_for_role(self, role_name: str) -> str:
        return DASHBOARD_ROUTES.get(role_name, "/")

    def _sanitize_cached_auth_result(self, otp_request_uuid, cached: dict | None) -> dict | None:
        """Drop stale biometric pending-auth cache when deployment policy disables biometrics."""
        if not cached:
            return None
        if not (cached.get("requires_biometric") or cached.get("requires_enrollment")):
            return cached

        from apps.accounts.repositories.auth_repository import OTPRequestRepository
        from apps.biometrics.services.policy_service import biometric_policy_service

        otp_req = OTPRequestRepository().get_by_uuid(otp_request_uuid)
        if otp_req and not biometric_policy_service.requires_verification_at_login(otp_req.user):
            self.otp_service.clear_auth_result(otp_request_uuid)
            return None
        return cached

    def student_login(
        self,
        index_number: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        user = self.user_repository.get_queryset().filter(
            index_number=index_number,
            role__name__in=self.STUDENT_ROLES,
        ).first()

        if not user or not user.check_password(password):
            self.mfa_service.log(
                event_type=MFALog.EventType.LOGIN_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"login_type": "student", "index_number": index_number},
            )
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        return self._initiate_otp_login(
            user=user,
            purpose=OTPRequest.Purpose.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def authenticate_student_for_ussd(
        self,
        index_number: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        """USSD channel authentication — password check only, no OTP step."""
        user = self.user_repository.get_queryset().filter(
            index_number=index_number,
            role__name__in=self.STUDENT_ROLES,
        ).first()

        if not user or not user.check_password(password):
            self.mfa_service.log(
                event_type=MFALog.EventType.LOGIN_FAILED,
                ip_address=ip_address,
                user_agent=user_agent or "ussd",
                metadata={"login_type": "ussd", "index_number": index_number},
            )
            raise AuthenticationError(
                message="Invalid index number or PIN.",
                code="invalid_credentials",
            )

        self.mfa_service.log(
            event_type=MFALog.EventType.LOGIN_SUCCESS,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or "ussd",
            metadata={"login_type": "ussd", "channel": "ussd"},
        )
        return user

    def admin_login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        user = self.user_repository.get_by_email(email)

        if not user or user.role.name != Role.Name.ADMIN:
            self._log_failed_admin_login(email, ip_address, user_agent, "admin")
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        if not user.check_password(password):
            self._log_failed_admin_login(email, ip_address, user_agent, "admin", user)
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        return self._initiate_otp_login(
            user=user,
            purpose=OTPRequest.Purpose.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def super_admin_login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        user = self.user_repository.get_by_email(email)

        if not user or user.role.name != Role.Name.SUPER_ADMIN:
            self._log_failed_admin_login(email, ip_address, user_agent, "super_admin")
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        if not user.check_password(password):
            self._log_failed_admin_login(email, ip_address, user_agent, "super_admin", user)
            raise AuthenticationError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="invalid_credentials",
            )

        self.mfa_service.log(
            event_type=MFALog.EventType.MFA_REQUIRED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"login_type": "super_admin"},
        )

        return self._initiate_otp_login(
            user=user,
            purpose=OTPRequest.Purpose.MFA,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_required=True,
        )

    def verify_otp_and_authenticate(
        self,
        otp_request_uuid,
        otp_code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        *,
        device_signals: dict | None = None,
        trusted_device_token: str | None = None,
        browser_fingerprint: str | None = None,
    ) -> dict:
        cached = self.otp_service.get_cached_auth_result(otp_request_uuid)
        cached = self._sanitize_cached_auth_result(otp_request_uuid, cached)
        if cached:
            return cached

        try:
            otp_request = self.otp_service.validate_code(
                otp_request_uuid=otp_request_uuid,
                code=otp_code,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except ValidationError as exc:
            if exc.code == "otp_already_used":
                cached = self.otp_service.get_cached_auth_result(otp_request_uuid)
                cached = self._sanitize_cached_auth_result(otp_request_uuid, cached)
                if cached:
                    return cached
            raise

        user = otp_request.user

        if not user.is_active:
            raise PermissionDeniedError(
                message="User account is deactivated.",
                code="account_deactivated",
            )

        signals = device_signals or {}
        resolved_fingerprint = browser_fingerprint or signals.get("browser_fingerprint", "")

        trusted_login = False
        try:
            from apps.biometrics.services.policy_service import biometric_policy_service
            from apps.biometrics.services.verification_service import biometric_verification_service
            from apps.trusted_devices.constants import RISK_ALLOW, RISK_BLOCK, RISK_REQUIRE_BIOMETRIC
            from apps.trusted_devices.services.risk_assessment_service import risk_assessment_service
            from apps.trusted_devices.services.trusted_device_service import trusted_device_service
            from apps.trusted_devices.utils import build_device_context

            if biometric_policy_service.requires_verification_at_login(user):
                from apps.biometrics.services.enrollment_service import biometric_enrollment_service

                profile_repo = biometric_verification_service.repository

                if not biometric_enrollment_service.has_active_biometric_profile(user):
                    pending = biometric_verification_service.create_pending_enrollment(
                        user=user,
                        otp_request_uuid=str(otp_request.uuid),
                    )
                    self.mfa_service.log(
                        event_type=MFALog.EventType.MFA_REQUIRED,
                        user=user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        metadata={"flow": "biometric_enrollment"},
                    )
                    result = {
                        "requires_enrollment": True,
                        "has_active_biometric_profile": False,
                        **pending,
                    }
                    self.otp_service.mark_consumed(
                        otp_request,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                    self.otp_service.cache_auth_result(otp_request_uuid, result)
                    return result

                profile = profile_repo.get_by_user(user)
                if profile and profile.is_active:
                    context = build_device_context(
                        user_agent=user_agent or "",
                        browser_fingerprint=resolved_fingerprint,
                        signals=signals,
                    )
                    decision = risk_assessment_service.assess_login(
                        user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        context=context,
                        trusted_device_token=trusted_device_token,
                    )

                    if decision.action == RISK_BLOCK:
                        self.mfa_service.log(
                            event_type=MFALog.EventType.LOGIN_FAILED,
                            user=user,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            metadata={"flow": "risk_blocked", "risk_score": decision.risk_score},
                        )
                        raise AuthenticationError(
                            message="Login blocked due to elevated security risk.",
                            code="login_blocked",
                        )

                    if decision.action == RISK_ALLOW and decision.trusted_device:
                        trusted_device_service.touch_device(
                            decision.trusted_device,
                            ip_address=ip_address,
                            context=context,
                            risk_score=decision.risk_score,
                        )
                        trusted_login = True
                    elif decision.action == RISK_REQUIRE_BIOMETRIC:
                        pending = biometric_verification_service.create_pending_auth(
                            user=user,
                            otp_request_uuid=str(otp_request.uuid),
                        )
                        self.mfa_service.log(
                            event_type=MFALog.EventType.MFA_REQUIRED,
                            user=user,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            metadata={
                                "flow": "biometric_verification",
                                "risk_score": decision.risk_score,
                                "reasons": decision.reasons,
                            },
                        )
                        result = {
                            "requires_biometric": True,
                            "has_active_biometric_profile": True,
                            "risk_score": decision.risk_score,
                            "risk_reasons": decision.reasons,
                            **pending,
                        }
                        self.otp_service.mark_consumed(
                            otp_request,
                            ip_address=ip_address,
                            user_agent=user_agent,
                        )
                        self.otp_service.cache_auth_result(otp_request_uuid, result)
                        return result
        except ImportError:
            pass

        session, tokens = self.session_service.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        event_type = MFALog.EventType.MFA_COMPLETED if otp_request.purpose == OTPRequest.Purpose.MFA else MFALog.EventType.LOGIN_SUCCESS
        self.mfa_service.log(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "session_uuid": str(session.uuid),
                "otp_purpose": otp_request.purpose,
            },
        )

        result = {
            "user_uuid": str(user.uuid),
            "session_uuid": str(session.uuid),
            "tokens": tokens,
            "redirect_path": self.dashboard_path_for_role(user.role.name),
            "trusted_login": trusted_login,
        }
        self.otp_service.mark_consumed(
            otp_request,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.otp_service.cache_auth_result(otp_request_uuid, result)
        return result

    def resend_otp(
        self,
        otp_request_uuid,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        from apps.accounts.repositories.auth_repository import OTPRequestRepository

        otp_repository = OTPRequestRepository()
        previous = otp_repository.get_by_uuid(otp_request_uuid)
        if not previous:
            from core.exceptions import NotFoundError

            raise NotFoundError(message="OTP request not found.", code="otp_not_found")

        if previous.is_verified:
            raise ValidationError(message="OTP has already been used.", code="otp_already_used")

        channel, recipient = self.otp_service.resolve_channel_and_recipient(previous.user)
        otp_request = self.otp_service.create_and_send(
            user=previous.user,
            purpose=previous.purpose,
            channel=channel,
            recipient=recipient,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {
            "otp_request_uuid": str(otp_request.uuid),
            "expires_at": otp_request.expires_at,
            "channel": otp_request.channel,
        }

    def _initiate_otp_login(
        self,
        user: User,
        purpose: str,
        ip_address: str | None,
        user_agent: str | None,
        mfa_required: bool = False,
    ) -> dict:
        if not user.is_active:
            raise PermissionDeniedError(
                message="User account is deactivated.",
                code="account_deactivated",
            )

        if not feature_flag_service.is_otp_enabled():
            return self._complete_password_login(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                mfa_completed=mfa_required or purpose == OTPRequest.Purpose.MFA,
            )

        channel, recipient = self.otp_service.resolve_channel_and_recipient(user)
        otp_request = self.otp_service.create_and_send(
            user=user,
            purpose=purpose,
            channel=channel,
            recipient=recipient,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        response = {
            "requires_otp": True,
            "otp_request_uuid": str(otp_request.uuid),
            "expires_at": otp_request.expires_at,
            "channel": otp_request.channel,
        }

        if mfa_required:
            response["mfa_required"] = True

        return response

    def _complete_password_login(
        self,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
        *,
        mfa_completed: bool = False,
    ) -> dict:
        session, tokens = self.session_service.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        event_type = (
            MFALog.EventType.MFA_COMPLETED if mfa_completed else MFALog.EventType.LOGIN_SUCCESS
        )
        self.mfa_service.log(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_uuid": str(session.uuid), "flow": "password_only"},
        )
        return {
            "user_uuid": str(user.uuid),
            "session_uuid": str(session.uuid),
            "tokens": tokens,
            "redirect_path": self.dashboard_path_for_role(user.role.name),
            "trusted_login": False,
        }

    def _log_failed_admin_login(
        self,
        email: str,
        ip_address: str | None,
        user_agent: str | None,
        login_type: str,
        user: User | None = None,
    ) -> None:
        self.mfa_service.log(
            event_type=MFALog.EventType.LOGIN_FAILED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"login_type": login_type, "email": email},
        )
