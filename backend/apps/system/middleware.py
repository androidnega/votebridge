import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from apps.accounts.models import Role


class MaintenanceModeMiddleware(MiddlewareMixin):
    """Block non–Super Admin traffic when maintenance mode is active."""

    EXEMPT_PREFIXES = (
        "/health/",
        "/admin/",
        "/api/v1/accounts/auth/",
        "/api/v1/system/maintenance/",
        "/api/v1/system/branding/",
        "/static/",
        "/media/",
    )

    def process_request(self, request):
        path = request.path
        if any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return None

        from apps.system.services.system_service import maintenance_service

        state = maintenance_service.get_state()
        if not state.get("is_enabled"):
            return None

        user = getattr(request, "user", None)
        role = getattr(getattr(user, "role", None), "name", None)
        if user and user.is_authenticated and role == Role.Name.SUPER_ADMIN:
            return None

        if path.startswith("/api/"):
            return JsonResponse(
                {
                    "success": False,
                    "error": {
                        "code": "maintenance_mode",
                        "message": state.get("message") or "VoteBridge is under maintenance.",
                    },
                },
                status=503,
            )
        return None
