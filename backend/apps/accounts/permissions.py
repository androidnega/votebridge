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


# Roles an election officer may look up when managing voters or nominating custodians.
ADMIN_USER_LOOKUP_ROLES = frozenset(
    {Role.Name.STUDENT, Role.Name.CANDIDATE, Role.Name.ADMIN}
)


class CanManageUsers(BasePermission):
    """Super Admin manages platform users. Admin may look up voters/custodians only."""

    message = "You do not have permission to manage users."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if role == Role.Name.SUPER_ADMIN:
            return True

        if role == Role.Name.ADMIN:
            return request.method in SAFE_METHODS and view.action in ("list", "retrieve")

        if view.action in ("retrieve", "list") and role in {
            Role.Name.STUDENT,
            Role.Name.CANDIDATE,
        }:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        role = _user_role_name(request.user)
        if role == Role.Name.SUPER_ADMIN:
            return True

        if role == Role.Name.ADMIN:
            target_role = getattr(getattr(obj, "role", None), "name", None)
            return target_role in ADMIN_USER_LOOKUP_ROLES

        if hasattr(obj, "uuid") and hasattr(request.user, "uuid"):
            return obj.uuid == request.user.uuid

        return False


class CanManageRoles(BasePermission):
    """Predefined roles only — Super Admin assigns privileged access."""

    message = "Super Admin access required to manage role assignments."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role_name(request.user) == Role.Name.SUPER_ADMIN
