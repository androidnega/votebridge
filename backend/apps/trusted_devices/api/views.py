from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.accounts.repositories.user_repository import UserRepository
from apps.biometrics.services.session_service import biometric_session_service
from apps.trusted_devices.api.serializers import DeviceRenameSerializer, DeviceRevokeSerializer
from apps.trusted_devices.constants import TRUSTED_DEVICE_COOKIE
from apps.trusted_devices.permissions import (
    CanManageOwnDevices,
    IsPrivilegedDeviceUser,
    TrustedDevicesModuleEnabled,
)
from apps.trusted_devices.services import (
    trusted_device_login_history_service,
    trusted_device_policy_service,
    trusted_device_service,
)
from apps.trusted_devices.utils import build_device_context, clear_trusted_device_cookie


def _serialize_device(device, *, is_current=False) -> dict:
    login_summary = trusted_device_login_history_service.serialize_device_login_summary(device)
    return {
        "uuid": str(device.uuid),
        "device_name": device.device_name,
        "device_type": device.device_type,
        "trust_level": device.trust_level,
        "browser_name": device.browser_name,
        "browser_version": device.browser_version,
        "operating_system": device.operating_system,
        "platform": device.platform,
        "last_country": device.last_country,
        "last_city": device.last_city,
        "last_ip": device.last_ip,
        "last_seen": device.last_seen,
        "previous_login_at": device.previous_login_at,
        "last_verified": device.last_verified,
        "last_biometric": device.last_biometric,
        "is_trusted": device.is_trusted,
        "is_revoked": device.is_revoked,
        "expires_at": device.expires_at,
        "risk_score": device.risk_score,
        "is_current": is_current,
        "login_summary": login_summary,
    }


class TrustedDeviceListView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def get(self, request):
        devices = trusted_device_service.list_devices(request.user)
        raw_token = request.COOKIES.get(TRUSTED_DEVICE_COOKIE)
        context = build_device_context(
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            browser_fingerprint=request.META.get("HTTP_X_DEVICE_FINGERPRINT", ""),
        )
        current = trusted_device_service.identify_current(request.user, raw_token, context)
        current_uuid = str(current.uuid) if current else None
        data = [
            _serialize_device(d, is_current=str(d.uuid) == current_uuid)
            for d in devices
        ]
        return Response({"success": True, "data": data})


class TrustedDeviceCurrentView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser]

    def get(self, request):
        raw_token = request.COOKIES.get(TRUSTED_DEVICE_COOKIE)
        context = build_device_context(
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            browser_fingerprint=request.META.get("HTTP_X_DEVICE_FINGERPRINT", ""),
        )
        device = trusted_device_service.identify_current(request.user, raw_token, context)
        if not device:
            return Response({"success": True, "data": None})
        return Response({"success": True, "data": _serialize_device(device, is_current=True)})


class TrustedDeviceHistoryView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def get(self, request, device_uuid):
        device = trusted_device_service.get_device(request.user, device_uuid)
        history = trusted_device_login_history_service.get_history(device, limit=20)
        data = [
            {
                "logged_in_at": h.logged_in_at,
                "country": h.country,
                "city": h.city,
                "browser_name": h.browser_name,
                "operating_system": h.operating_system,
                "authentication_method": h.authentication_method,
                "risk_score": h.risk_score,
            }
            for h in history
        ]
        return Response({"success": True, "data": data})


class TrustedDeviceRenameView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def patch(self, request, device_uuid):
        serializer = DeviceRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = trusted_device_service.rename_device(
            request.user,
            device_uuid,
            serializer.validated_data["device_name"],
        )
        return Response({"success": True, "data": _serialize_device(device)})


class TrustedDeviceRevokeView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def post(self, request, device_uuid):
        serializer = DeviceRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_user = request.user
        if serializer.validated_data.get("user_uuid") and request.user.role.name == Role.Name.SUPER_ADMIN:
            found = UserRepository().get_by_uuid(serializer.validated_data["user_uuid"])
            if found:
                target_user = found
        device = trusted_device_service.revoke_device(request.user, device_uuid, target_user=target_user)

        raw_token = request.COOKIES.get(TRUSTED_DEVICE_COOKIE)
        context = build_device_context(
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            browser_fingerprint=request.META.get("HTTP_X_DEVICE_FINGERPRINT", ""),
        )
        current = trusted_device_service.identify_current(request.user, raw_token, context)
        response = Response({"success": True, "data": _serialize_device(device)})
        if current and str(current.uuid) == str(device.uuid):
            clear_trusted_device_cookie(response)
        return response


class TrustedDeviceDeleteView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def delete(self, request, device_uuid):
        trusted_device_service.remove_device(request.user, device_uuid)
        return Response({"success": True, "data": {"deleted": True}})


class TrustedDeviceAssignUniversityView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser]

    def post(self, request, device_uuid):
        device = trusted_device_service.assign_university_managed(request.user, device_uuid)
        return Response({"success": True, "data": _serialize_device(device)})


class TrustedDevicePolicyView(APIView):
    permission_classes = [IsAuthenticated, IsPrivilegedDeviceUser]

    def get(self, request):
        return Response({"success": True, "data": trusted_device_policy_service.get_policy()})


class TrustedDeviceSessionStatusView(APIView):
    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser]

    def get(self, request):
        token = request.headers.get("X-High-Assurance-Token") or request.query_params.get("high_assurance_token")
        status_data = biometric_session_service.get_session_status(request.user, token=token)
        return Response({"success": True, "data": status_data})


class TrustedDeviceForceReverifyView(APIView):
    """Mark current session for mandatory biometric on next login."""

    permission_classes = [IsAuthenticated, TrustedDevicesModuleEnabled, IsPrivilegedDeviceUser, CanManageOwnDevices]

    def post(self, request):
        raw_token = request.COOKIES.get(TRUSTED_DEVICE_COOKIE)
        if raw_token:
            device = trusted_device_service.validate_token(
                request.user,
                raw_token,
                build_device_context(
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    browser_fingerprint=request.META.get("HTTP_X_DEVICE_FINGERPRINT", ""),
                ),
            )
            if device:
                trusted_device_service.revoke_device(request.user, device.uuid)
        response = Response({"success": True, "data": {"reverification_required": True}})
        clear_trusted_device_cookie(response)
        return response
