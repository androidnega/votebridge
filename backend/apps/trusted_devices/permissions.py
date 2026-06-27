from rest_framework.permissions import BasePermission

from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin, _user_role_name
from apps.biometrics.services.audit_service import biometric_audit_service
from apps.trusted_devices.services.policy_service import trusted_device_policy_service


class TrustedDevicesModuleEnabled(BasePermission):
    message = "Trusted devices module is disabled."

    def has_permission(self, request, view):
        return trusted_device_policy_service.is_enabled()


class IsPrivilegedDeviceUser(BasePermission):
    message = "Trusted devices are only available for privileged staff."

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and biometric_audit_service.is_privileged_user(user)


class CanManageOwnDevices(BasePermission):
    def has_permission(self, request, view):
        policy = trusted_device_policy_service.get_policy()
        return policy.get("enable_administrator_device_management", True)


class CanRevokeAnyDevice(IsSuperAdmin):
    pass


class CanViewTrustedDeviceSettings(IsSuperAdmin):
    pass
