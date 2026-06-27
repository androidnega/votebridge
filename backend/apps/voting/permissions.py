from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name


class CanVote(BasePermission):
    """Students and candidates who are authenticated may access voting endpoints."""

    message = "Only eligible voters can access voting."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = _user_role_name(request.user)
        return role in {Role.Name.STUDENT, Role.Name.CANDIDATE}
