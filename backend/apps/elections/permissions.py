from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import Role
from apps.accounts.permissions import IsElectionAdministrator, _user_role_name


class CanManageElections(BasePermission):
    """Election Administrators manage elections; authenticated users may read."""

    message = "Election Administrator access required to manage elections."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True

        action = getattr(view, "action", None)
        if action in ("list", "retrieve", None) and request.method in SAFE_METHODS:
            return True

        return role == Role.Name.ADMIN


class CanManageCandidates(BasePermission):
    """Election Administrators manage candidates; others read only."""

    message = "Election Administrator access required to manage candidates."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True

        return role == Role.Name.ADMIN


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
    message = "Election Administrator access required to manage positions."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return True
        return role == Role.Name.ADMIN


class CanManageVoterEligibility(BasePermission):
    message = "Election Administrator access required to manage voter eligibility."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = _user_role_name(request.user)
        if request.method in SAFE_METHODS:
            return role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}
        return role == Role.Name.ADMIN


# Re-export for convenience in other apps
IsElectionOfficer = IsElectionAdministrator
