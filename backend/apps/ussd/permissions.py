from django.conf import settings
from rest_framework.permissions import AllowAny, BasePermission

from apps.accounts.permissions import IsAdminOrSuperAdmin


class CanViewUssdMonitoring(IsAdminOrSuperAdmin):
    message = "Admin access required to view USSD monitoring."


class UssdCallbackPermission(BasePermission):
    """Arkesel callbacks — optional shared secret when configured."""

    message = "Invalid USSD callback credentials."

    def has_permission(self, request, view):
        secret = getattr(settings, "ARKESEL_USSD_CALLBACK_SECRET", "")
        if not secret:
            return True
        provided = (
            request.headers.get("X-Arkesel-Secret")
            or request.META.get("HTTP_X_ARKESEL_SECRET")
            or request.POST.get("secret", "")
        )
        return provided == secret
