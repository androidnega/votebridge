from rest_framework.permissions import AllowAny, BasePermission

from apps.accounts.permissions import IsAdminOrSuperAdmin


class CanViewUssdMonitoring(IsAdminOrSuperAdmin):
    message = "Admin access required to view USSD monitoring."


class UssdCallbackPermission(AllowAny):
    """Arkesel callbacks are unauthenticated; validate via rate limits and session IDs."""

    pass
