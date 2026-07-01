from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.repositories.user_repository import UserRepository
from apps.biometrics.api.serializers import (
    BiometricChallengeRequestSerializer,
    BiometricEnrollLoginSerializer,
    BiometricEnrollmentSerializer,
    BiometricResetConfirmSerializer,
    BiometricResetRequestSerializer,
    BiometricStepUpSerializer,
    BiometricVerifyLoginSerializer,
)
from apps.biometrics.permissions import (
    BiometricsModuleEnabled,
    CanAccessBiometricSettings,
    CanEnrollBiometrics,
    CanManageBiometrics,
    CanViewBiometricHistory,
    IsPrivilegedBiometricUser,
)
from apps.biometrics.repositories.biometric_repository import BiometricVerificationLogRepository
from apps.biometrics.services import (
    biometric_enrollment_service,
    biometric_policy_service,
    biometric_session_service,
    biometric_verification_service,
    challenge_generator_service,
)
from core.client_meta import get_client_ip


def _client_meta(request) -> tuple:
    return get_client_ip(request), request.META.get("HTTP_USER_AGENT", "")


def _device_fingerprint(request) -> str:
    return request.META.get("HTTP_X_DEVICE_FINGERPRINT", "")


class BiometricEnrollmentView(APIView):
    permission_classes = [IsAuthenticated, BiometricsModuleEnabled, CanEnrollBiometrics]

    def get(self, request):
        return Response({"success": True, "data": biometric_enrollment_service.get_enrollment_requirements()})

    def post(self, request):
        serializer = BiometricEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = UserRepository().get_by_uuid(serializer.validated_data["user_uuid"])
        if not target:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "User not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        ip, ua = _client_meta(request)
        result = biometric_enrollment_service.enroll(
            actor=request.user,
            target_user=target,
            images=serializer.validated_data["images"],
            ip_address=ip,
            user_agent=ua,
            device_fingerprint=_device_fingerprint(request),
        )
        return Response({"success": True, "data": result}, status=status.HTTP_201_CREATED)


class BiometricEnrollLoginView(APIView):
    permission_classes = [AllowAny, BiometricsModuleEnabled]

    def post(self, request):
        serializer = BiometricEnrollLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip, ua = _client_meta(request)
        result = biometric_enrollment_service.enroll_from_pending_auth(
            pending_auth_token=serializer.validated_data["pending_auth_token"],
            images=serializer.validated_data["images"],
            ip_address=ip,
            user_agent=ua,
            device_fingerprint=_device_fingerprint(request),
            device_signals=serializer.validated_data.get("device_signals"),
        )
        return Response({"success": True, "data": result}, status=status.HTTP_201_CREATED)


class BiometricResetOtpView(APIView):
    permission_classes = [IsAuthenticated, BiometricsModuleEnabled, IsPrivilegedBiometricUser]

    def post(self, request):
        serializer = BiometricResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["password"]):
            return Response(
                {"success": False, "error": {"code": "invalid_password", "message": "Invalid password."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not biometric_enrollment_service.has_active_biometric_profile(request.user):
            return Response(
                {"success": False, "error": {"code": "not_enrolled", "message": "No biometric profile enrolled."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.accounts.models import OTPRequest
        from apps.accounts.services.otp_service import OTPService

        otp_service = OTPService()
        channel, recipient = otp_service.resolve_channel_and_recipient(request.user)
        ip, ua = _client_meta(request)
        otp_request = otp_service.create_and_send(
            user=request.user,
            purpose=OTPRequest.Purpose.MFA,
            channel=channel,
            recipient=recipient,
            ip_address=ip,
            user_agent=ua,
        )
        return Response(
            {
                "success": True,
                "data": {
                    "otp_request_uuid": str(otp_request.uuid),
                    "expires_at": otp_request.expires_at,
                    "channel": otp_request.channel,
                },
            }
        )


class BiometricResetView(APIView):
    permission_classes = [IsAuthenticated, BiometricsModuleEnabled, IsPrivilegedBiometricUser]

    def post(self, request):
        serializer = BiometricResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip, ua = _client_meta(request)
        result = biometric_enrollment_service.reset_profile(
            user=request.user,
            password=serializer.validated_data["password"],
            otp_request_uuid=serializer.validated_data["otp_request_uuid"],
            otp_code=serializer.validated_data["otp_code"],
            ip_address=ip,
            user_agent=ua,
            device_fingerprint=_device_fingerprint(request),
        )
        return Response({"success": True, "data": result})


class BiometricVerifyLoginView(APIView):
    permission_classes = [AllowAny, BiometricsModuleEnabled]

    def post(self, request):
        serializer = BiometricVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip, ua = _client_meta(request)
        result = biometric_verification_service.verify_login(
            pending_auth_token=serializer.validated_data["pending_auth_token"],
            challenge_id=serializer.validated_data["challenge_id"],
            frames=serializer.validated_data["frames"],
            ip_address=ip,
            user_agent=ua,
            device_fingerprint=_device_fingerprint(request),
            device_signals=serializer.validated_data.get("device_signals"),
        )
        raw_token = result.pop("_trusted_device_token", "")
        cookie_max_age = result.pop("_cookie_max_age_seconds", 0)
        response = Response({"success": True, "data": result}, status=status.HTTP_200_OK)
        if raw_token and cookie_max_age:
            from apps.trusted_devices.utils import set_trusted_device_cookie

            set_trusted_device_cookie(response, raw_token, cookie_max_age)
        return response


class BiometricStepUpView(APIView):
    permission_classes = [IsAuthenticated, BiometricsModuleEnabled, IsPrivilegedBiometricUser]

    def post(self, request):
        serializer = BiometricStepUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip, ua = _client_meta(request)
        result = biometric_verification_service.verify_step_up(
            user=request.user,
            challenge_id=serializer.validated_data["challenge_id"],
            frames=serializer.validated_data["frames"],
            action=serializer.validated_data["action"],
            ip_address=ip,
            user_agent=ua,
            device_fingerprint=_device_fingerprint(request),
        )
        return Response({"success": True, "data": result})


class BiometricChallengeView(APIView):
    permission_classes = [AllowAny, BiometricsModuleEnabled]

    def post(self, request):
        serializer = BiometricChallengeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pending_token = serializer.validated_data.get("pending_auth_token")

        if pending_token:
            user = biometric_verification_service.resolve_pending_user(pending_token)
        elif request.user and request.user.is_authenticated:
            user = request.user
        else:
            return Response(
                {"success": False, "error": {"code": "auth_required", "message": "Authentication required."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        challenge = challenge_generator_service.generate(user)
        return Response({"success": True, "data": challenge})


class BiometricStatusView(APIView):
    permission_classes = [IsAuthenticated, BiometricsModuleEnabled]

    def get(self, request):
        data = biometric_verification_service.get_status(request.user)
        return Response({"success": True, "data": data})


class BiometricSettingsView(APIView):
    permission_classes = [IsAuthenticated, CanAccessBiometricSettings]

    def get(self, request):
        return Response({"success": True, "data": biometric_policy_service.get_policy()})


class BiometricHistoryView(APIView):
    permission_classes = [IsAuthenticated, CanViewBiometricHistory]

    def get(self, request):
        repo = BiometricVerificationLogRepository()
        user_uuid = request.query_params.get("user_uuid")
        target_user = request.user
        if user_uuid and request.user.role.name == "super_admin":
            target = UserRepository().get_by_uuid(user_uuid)
            if target:
                target_user = target

        logs = repo.list_for_user(target_user, limit=int(request.query_params.get("limit", 50)))
        data = [
            {
                "uuid": str(log.uuid),
                "event_type": log.event_type,
                "outcome": log.outcome,
                "challenge_type": log.challenge_type,
                "confidence": log.confidence,
                "liveness_score": log.liveness_score,
                "processing_time_ms": log.processing_time_ms,
                "model_version": log.model_version,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in logs
        ]
        return Response({"success": True, "data": data})


class BiometricSessionValidateView(APIView):
    permission_classes = [IsAuthenticated, IsPrivilegedBiometricUser]

    def post(self, request):
        token = request.data.get("high_assurance_token", "")
        biometric_session_service.validate_session(request.user, token)
        return Response({"success": True, "data": {"valid": True}})


class BiometricSessionStatusView(APIView):
    permission_classes = [IsAuthenticated, IsPrivilegedBiometricUser]

    def get(self, request):
        token = request.headers.get("X-High-Assurance-Token") or request.query_params.get("high_assurance_token")
        data = biometric_session_service.get_session_status(request.user, token=token)
        return Response({"success": True, "data": data})
