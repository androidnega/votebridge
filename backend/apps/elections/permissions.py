from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name


class CanManageElections(BasePermission):
    """Admin and Super Admin can manage elections; authenticated users can read."""

    message = "Admin or Super Admin access required to manage elections."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True

        action = getattr(view, "action", None)
        if action in ("list", "retrieve", None) and request.method in SAFE_METHODS:
            return True

        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanManageCandidates(BasePermission):
    """Admin and Super Admin manage candidates; others read only."""

    message = "Admin or Super Admin access required to manage candidates."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True

        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanManageVotingChannels(BasePermission):
    message = "Super Admin access required to manage voting channels."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}
        return role == Role.Name.SUPER_ADMIN


class CanManagePositions(BasePermission):
    message = "Admin or Super Admin access required to manage positions."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}


class CanManageVoterEligibility(BasePermission):
    message = "Admin or Super Admin access required to manage voter eligibility."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}
        return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}
