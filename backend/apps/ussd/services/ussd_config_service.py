import logging
import urllib.error
import urllib.request

from django.conf import settings

from apps.ussd.models import USSDRequestLog
from apps.ussd.repositories.ussd_repository import USSDRequestLogRepository
from core.public_urls import USSD_CALLBACK_PATH, build_public_url, get_public_base_url

logger = logging.getLogger("votebridge")


class UssdConfigService:
    """Operational USSD integration metadata — no business rules."""

    def __init__(self, log_repository: USSDRequestLogRepository | None = None):
        self.log_repository = log_repository or USSDRequestLogRepository()

    def get_callback_url(self) -> str:
        return build_public_url(USSD_CALLBACK_PATH)

    def get_callback_path(self) -> str:
        return USSD_CALLBACK_PATH

    def get_environment(self) -> str:
        if settings.DEBUG:
            return "development"
        return "production"

    def get_provider_user_id(self) -> str:
        return getattr(settings, "ARKESEL_USSD_USER_ID", "VOTEBRIDGE")

    def get_integration_config(self) -> dict:
        health = self.get_health_snapshot()
        return {
            "callback_url": self.get_callback_url(),
            "callback_path": self.get_callback_path(),
            "public_base_url": get_public_base_url(),
            "environment": self.get_environment(),
            "provider_user_id": self.get_provider_user_id(),
            "health_status": health["status"],
            "health": health,
        }

    def get_health_snapshot(self) -> dict:
        logs = self.log_repository.get_queryset()
        last_log = logs.order_by("-created_at").first()
        last_success = logs.filter(outcome=USSDRequestLog.Outcome.SUCCESS).order_by("-created_at").first()
        last_failed = logs.filter(outcome=USSDRequestLog.Outcome.ERROR).order_by("-created_at").first()

        return {
            "callback_url": self.get_callback_url(),
            "reachable": self._probe_reachability(),
            "last_callback_at": last_log.created_at.isoformat() if last_log else None,
            "last_successful_callback_at": last_success.created_at.isoformat() if last_success else None,
            "last_failed_callback_at": last_failed.created_at.isoformat() if last_failed else None,
            "last_http_status": last_log.http_status if last_log else None,
            "last_processing_duration_ms": last_log.duration_ms if last_log else None,
            "status": self._derive_health_status(last_log, last_failed),
        }

    def _derive_health_status(
        self,
        last_log: USSDRequestLog | None,
        last_failed: USSDRequestLog | None,
    ) -> str:
        if not get_public_base_url():
            return "unconfigured"
        if not last_log:
            return "pending"
        reachability = self._probe_reachability()
        if reachability == "unreachable":
            return "degraded"
        if last_log.outcome == USSDRequestLog.Outcome.ERROR:
            return "degraded"
        if last_failed and last_failed.created_at == last_log.created_at:
            return "degraded"
        return "healthy"

    def _probe_reachability(self) -> str:
        if not get_public_base_url():
            return "unconfigured"
        url = self.get_callback_url()
        try:
            request = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(request, timeout=3) as response:
                if response.status == 200:
                    return "reachable"
                return "degraded"
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            logger.debug("USSD callback reachability probe failed: %s", exc)
            return "unreachable"


ussd_config_service = UssdConfigService()
