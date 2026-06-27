from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin, _user_role_name
from apps.results.models import ElectionResult


class CanGenerateResults(IsAdminOrSuperAdmin):
    message = "Admin access required to generate results."


class CanViewResultReports(IsAdminOrSuperAdmin):
    message = "Admin access required to view result reports."


class CanCertifyResults(IsSuperAdmin):
    message = "Super Admin access required to certify results."


class CanPublishResults(IsSuperAdmin):
    message = "Super Admin access required to publish results."


class CanArchiveResults(IsSuperAdmin):
    message = "Super Admin access required to archive results."


class CanViewPublishedResults(BasePermission):
    """Students may view published results; admins may view all non-pending states."""

    message = "You do not have permission to view these results."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj: ElectionResult) -> bool:
        role = _user_role_name(request.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return True
        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            return obj.status == ElectionResult.Status.PUBLISHED
        return False
