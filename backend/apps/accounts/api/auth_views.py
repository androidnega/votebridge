from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.auth_serializers import (
    AdminLoginSerializer,
    AuthOTPChallengeSerializer,
    AuthSuccessSerializer,
    LogoutSerializer,
    MFALogSerializer,
    OTPResendSerializer,
    OTPVerifySerializer,
    SessionSerializer,
    StudentLoginSerializer,
    SuperAdminLoginSerializer,
    TokenRefreshSerializer,
    UniversalLoginSerializer,
)
from apps.accounts.permissions import IsAdminOrSuperAdmin
from apps.accounts.services import auth_service, mfa_service, session_service
from apps.accounts.services.token_service import TokenService
from apps.accounts.throttles import LoginRateThrottle, OTPRateThrottle, TokenRefreshRateThrottle
from apps.trusted_devices.constants import TRUSTED_DEVICE_COOKIE
from apps.trusted_devices.utils import clear_trusted_device_cookie
from core.client_meta import get_browser_fingerprint


def _client_meta(request) -> tuple:
    ip_address = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return ip_address, user_agent


class UniversalLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = UniversalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.login(
            identity=serializer.validated_data["identity"],
            password=serializer.validated_data["password"],
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": AuthOTPChallengeSerializer(result).data},
            status=status.HTTP_200_OK,
        )


class StudentLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.student_login(
            **serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": AuthOTPChallengeSerializer(result).data},
            status=status.HTTP_200_OK,
        )


class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.admin_login(
            **serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": AuthOTPChallengeSerializer(result).data},
            status=status.HTTP_200_OK,
        )


class SuperAdminLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = SuperAdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.super_admin_login(
            **serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": AuthOTPChallengeSerializer(result).data},
            status=status.HTTP_200_OK,
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.verify_otp_and_authenticate(
            otp_request_uuid=serializer.validated_data["otp_request_uuid"],
            otp_code=serializer.validated_data["otp_code"],
            ip_address=ip_address,
            user_agent=user_agent,
            device_signals=serializer.validated_data.get("device_signals"),
            trusted_device_token=request.COOKIES.get(TRUSTED_DEVICE_COOKIE),
            browser_fingerprint=get_browser_fingerprint(request) or "",
        )
        response = Response(
            {"success": True, "data": AuthSuccessSerializer(result).data},
            status=status.HTTP_200_OK,
        )
        return response


class OTPResendView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = OTPResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = auth_service.resend_otp(
            otp_request_uuid=serializer.validated_data["otp_request_uuid"],
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": result},
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [TokenRefreshRateThrottle]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        token_service = TokenService()
        tokens = token_service.refresh(
            refresh_token_str=serializer.validated_data["refresh"],
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response({"success": True, "data": tokens}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)

        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import RefreshToken

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            session_service.logout(
                jti=str(refresh["jti"]),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except TokenError:
            pass

        response = Response(
            {"success": True, "data": {"message": "Logged out successfully."}},
            status=status.HTTP_200_OK,
        )
        try:
            from apps.trusted_devices.services.policy_service import trusted_device_policy_service
            from apps.trusted_devices.utils import clear_trusted_device_cookie

            if trusted_device_policy_service.get_policy().get("invalidate_trusted_device_on_logout"):
                clear_trusted_device_cookie(response)
        except ImportError:
            pass
        return response


class CurrentUserView(APIView):
    """Authenticated user's own profile — no user UUID required in the URL."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.accounts.api.serializers import UserSerializer

        user = request.user
        if not hasattr(user, "role"):
            from apps.accounts.models import User as UserModel

            user = UserModel.objects.select_related("role").get(pk=user.pk)
        return Response({"success": True, "data": UserSerializer(user).data})

    def patch(self, request):
        from apps.accounts.api.serializers import UserSerializer, UserUpdateSerializer
        from apps.accounts.services import user_service

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "index_number",
            "student_id",
        }
        payload = {key: value for key, value in request.data.items() if key in allowed_fields}
        serializer = UserUpdateSerializer(data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        user = user_service.update_user(request.user.uuid, serializer.validated_data)
        return Response({"success": True, "data": UserSerializer(user).data})


class SessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = session_service.list_sessions(request.user)
        data = [
            {
                "uuid": s.uuid,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "is_active": s.is_active,
                "expires_at": s.expires_at,
                "last_activity_at": s.last_activity_at,
                "created_at": s.created_at,
            }
            for s in sessions
        ]
        return Response(
            {"success": True, "data": SessionSerializer(data, many=True).data},
            status=status.HTTP_200_OK,
        )


class SessionRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        ip_address, user_agent = _client_meta(request)
        session = session_service.revoke_session(
            session_uuid=uuid,
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        data = {
            "uuid": session.uuid,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "is_active": session.is_active,
            "expires_at": session.expires_at,
            "last_activity_at": session.last_activity_at,
            "created_at": session.created_at,
        }
        return Response(
            {"success": True, "data": SessionSerializer(data).data},
            status=status.HTTP_200_OK,
        )


class MFALogListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        user_uuid = request.query_params.get("user_uuid")
        if user_uuid:
            from apps.accounts.services import user_service

            user = user_service.get_user(user_uuid)
            logs = mfa_service.list_logs(user=user)
        else:
            logs = mfa_service.list_logs()

        data = [
            {
                "uuid": log.uuid,
                "event_type": log.event_type,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.metadata,
                "created_at": log.created_at,
            }
            for log in logs
        ]
        return Response(
            {"success": True, "data": MFALogSerializer(data, many=True).data},
            status=status.HTTP_200_OK,
        )
