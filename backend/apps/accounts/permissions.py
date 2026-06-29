from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import Role


def _user_role_name(user) -> str | None:
    if not user.is_authenticated:
        return None
    if not hasattr(user, "role"):
        return None
    return user.role.name


class IsSuperAdmin(BasePermission):
    message = "Super Admin access required."

    def has_permission(self, request, view):
        return _user_role_name(request.user) == Role.Name.SUPER_ADMIN


class IsAdminOrSuperAdmin(BasePermission):
    message = "Admin or Super Admin access required."

    def has_permission(self, request, view):
        role = _user_role_name(request.user)
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class IsElectionAdministrator(BasePermission):
    """Election Officer (admin) — operational election management only."""

    message = "Election Administrator access required."

    def has_permission(self, request, view):
        return _user_role_name(request.user) == Role.Name.ADMIN


class CanManageUsers(BasePermission):
    """Admin and Super Admin can manage users; others can only read their own profile."""

    message = "You do not have permission to manage users."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return True

        if view.action in ("retrieve", "list") and role in {
            Role.Name.STUDENT,
            Role.Name.CANDIDATE,
        }:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        role = _user_role_name(request.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return True

        if hasattr(obj, "uuid") and hasattr(request.user, "uuid"):
            return obj.uuid == request.user.uuid

        return False


class CanManageRoles(BasePermission):
    message = "Super Admin access required to manage roles."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return role in {
                Role.Name.ADMIN,
                Role.Name.SUPER_ADMIN,
            }
        return role == Role.Name.SUPER_ADMIN
