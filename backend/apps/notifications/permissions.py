from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin, _user_role_name


class CanViewCommunications(IsAdminOrSuperAdmin):
    message = "Admin access required to view communications."


class CanManageCommunications(IsSuperAdmin):
    message = "Super Admin access required to manage communications."


class CanManageCommunicationSettings(IsAdminOrSuperAdmin):
    message = "Admin access required to manage communication settings."


class CanViewOwnNotifications(BasePermission):
    message = "Authentication required."

    def has_permission(self, request, view):
        return request.user.is_authenticated
