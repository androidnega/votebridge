from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name


class CanRequestSVT(BasePermission):
    """Students and candidates may request SVTs for elections they are eligible for."""

    message = "Only eligible voters can request voting tokens."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        return role in {Role.Name.STUDENT, Role.Name.CANDIDATE}


class CanManageSVT(BasePermission):
    """Admins and super admins can view, revoke, and reissue SVTs."""

    message = "Admin or Super Admin access required to manage SVTs."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanViewSecurityMonitoring(BasePermission):
    message = "Admin or Super Admin access required to view security monitoring."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanManageSecurityAlerts(CanViewSecurityMonitoring):
    message = "Admin or Super Admin access required to manage security alerts."
