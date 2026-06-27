from rest_framework.permissions import BasePermission

from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin, _user_role_name
from apps.biometrics.services.audit_service import biometric_audit_service
from apps.biometrics.services.policy_service import biometric_policy_service


class BiometricsModuleEnabled(BasePermission):
    message = "Biometrics module is disabled."

    def has_permission(self, request, view):
        return biometric_policy_service.is_module_enabled()


class IsPrivilegedBiometricUser(BasePermission):
    message = "Biometrics are only available for privileged staff accounts."

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and biometric_audit_service.is_privileged_user(user)


class CanEnrollBiometrics(BasePermission):
    message = "Only Super Admin can enroll biometric profiles."

    def has_permission(self, request, view):
        return _user_role_name(request.user) == "super_admin"


class CanManageBiometrics(IsAdminOrSuperAdmin):
    pass


class CanViewBiometricHistory(IsAdminOrSuperAdmin):
    pass


class CanAccessBiometricSettings(IsSuperAdmin):
    pass
