from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name


class CanViewFraudCases(BasePermission):
    message = "Admin or Super Admin access required to view fraud cases."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanManageFraudCases(CanViewFraudCases):
    message = "Admin or Super Admin access required to manage fraud cases."
