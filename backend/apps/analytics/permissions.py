from apps.accounts.permissions import IsAdminOrSuperAdmin
from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name


CanAccessAnalytics = IsAdminOrSuperAdmin


class CanAccessPersonalAnalytics(BasePermission):
    """Students and candidates may access personal analytics only."""

    message = "You do not have permission to view these analytics."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return True
        return role in {Role.Name.STUDENT, Role.Name.CANDIDATE}
