import logging
import time
from datetime import timedelta

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from apps.dashboard.services.dashboard_service import dashboard_service
from apps.elections.models import Election
from apps.fraud.services.alert_service import audit_log_service
from apps.notifications.services.communication_service import communication_service
from apps.operations.repositories.operations_repository import OperationsRepository
from apps.results.repositories.election_result_repository import ElectionResultRepository
from apps.ussd.repositories.ussd_repository import USSDSessionRepository
from core.realtime.sanitize import sanitize_payload

logger = logging.getLogger("votebridge")

CACHE_TTL = 30
OVERVIEW_CACHE_KEY = "operations:overview"
HEALTH_CACHE_KEY = "operations:health"
PERFORMANCE_CACHE_KEY = "operations:performance"

HEALTH_STATUSES = ("healthy", "warning", "critical", "unknown")


class OperationsHealthService:
    """Infrastructure health probes for the EOC."""

    def __init__(self, repository: OperationsRepository | None = None):
        self.repository = repository or OperationsRepository()

    def check_all(self) -> dict:
        cached = cache.get(HEALTH_CACHE_KEY)
        if cached:
            return cached

        checked_at = timezone.now().isoformat()
        components = [
            self._check_database(checked_at),
            self._check_redis(checked_at),
            self._check_websockets(checked_at),
            self._check_workers(checked_at),
            self._check_communications_providers(checked_at),
            self._check_ussd(checked_at),
            self._check_cpu(checked_at),
            self._check_memory(checked_at),
            self._check_storage(checked_at),
        ]
        overall = self._overall_status(components)
        payload = {
            "overall_status": overall,
            "checked_at": checked_at,
            "components": components,
        }
        cache.set(HEALTH_CACHE_KEY, payload, CACHE_TTL)
        return payload

    def _overall_status(self, components: list[dict]) -> str:
        statuses = {c["status"] for c in components}
        if "critical" in statuses:
            return "critical"
        if "warning" in statuses:
            return "warning"
        if statuses == {"unknown"}:
            return "unknown"
        return "healthy"

    def _component(self, name: str, status: str, checked_at: str, **extra) -> dict:
        return {
            "name": name,
            "status": status if status in HEALTH_STATUSES else "unknown",
            "checked_at": checked_at,
            **extra,
        }

    def _check_database(self, checked_at: str) -> dict:
        start = time.perf_counter()
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            status = "warning" if elapsed_ms > 500 else "healthy"
            return self._component(
                "database",
                status,
                checked_at,
                response_time_ms=elapsed_ms,
                details="PostgreSQL connection OK",
            )
        except Exception as exc:
            logger.warning("Operations health DB check failed: %s", exc)
            return self._component(
                "database",
                "critical",
                checked_at,
                response_time_ms=None,
                details=str(exc),
            )

    def _check_redis(self, checked_at: str) -> dict:
        start = time.perf_counter()
        try:
            cache.set("operations:health:ping", "1", 5)
            ok = cache.get("operations:health:ping") == "1"
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            status = "healthy" if ok else "critical"
            return self._component(
                "redis",
                status,
                checked_at,
                response_time_ms=elapsed_ms,
                details="Redis cache reachable",
            )
        except Exception as exc:
            return self._component("redis", "critical", checked_at, details=str(exc))

    def _check_websockets(self, checked_at: str) -> dict:
        try:
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer is None:
                return self._component("websockets", "unknown", checked_at, details="No channel layer configured")
            return self._component("websockets", "healthy", checked_at, details="Django Channels layer active")
        except Exception as exc:
            return self._component("websockets", "warning", checked_at, details=str(exc))

    def _check_workers(self, checked_at: str) -> dict:
        comms = communication_service.get_dashboard()
        pending = comms.get("pending_queue", 0)
        retry = comms.get("retry_queue", 0)
        status = "warning" if pending + retry > 100 else "healthy"
        return self._component(
            "queue_workers",
            status,
            checked_at,
            details=f"Pending {pending}, retry {retry}",
            pending_jobs=pending,
            retry_jobs=retry,
        )

    def _check_communications_providers(self, checked_at: str) -> dict:
        dashboard = communication_service.get_dashboard()
        providers = dashboard.get("providers") or []
        if not providers:
            return self._component("sms_email", "unknown", checked_at, details="No providers configured")

        disconnected = [p for p in providers if p.get("connection_status") != "connected"]
        sms_status = "healthy" if not disconnected else "warning"
        email_status = sms_status
        return self._component(
            "communications",
            sms_status,
            checked_at,
            sms_status=sms_status,
            email_status=email_status,
            details=f"{len(providers) - len(disconnected)}/{len(providers)} providers connected",
        )

    def _check_ussd(self, checked_at: str) -> dict:
        stats = USSDSessionRepository().dashboard_stats()
        failed = stats.get("failed_sessions", 0)
        active = stats.get("active_sessions", 0)
        status = "warning" if failed > active and failed > 5 else "healthy"
        return self._component(
            "ussd",
            status,
            checked_at,
            details=f"Active sessions: {active}, failed: {failed}",
        )

    def _check_cpu(self, checked_at: str) -> dict:
        if not psutil:
            return self._component("cpu", "unknown", checked_at, details="psutil not installed")
        try:
            percent = psutil.cpu_percent(interval=0.1)
            status = "critical" if percent > 90 else "warning" if percent > 75 else "healthy"
            return self._component("cpu", status, checked_at, usage_percent=percent)
        except Exception:
            return self._component("cpu", "unknown", checked_at)

    def _check_memory(self, checked_at: str) -> dict:
        if not psutil:
            return self._component("memory", "unknown", checked_at, details="psutil not installed")
        try:
            mem = psutil.virtual_memory()
            status = "critical" if mem.percent > 90 else "warning" if mem.percent > 80 else "healthy"
            return self._component("memory", status, checked_at, usage_percent=mem.percent)
        except Exception:
            return self._component("memory", "unknown", checked_at)

    def _check_storage(self, checked_at: str) -> dict:
        if not psutil:
            return self._component("storage", "unknown", checked_at, details="psutil not installed")
        try:
            disk = psutil.disk_usage("/")
            status = "critical" if disk.percent > 90 else "warning" if disk.percent > 80 else "healthy"
            return self._component("storage", status, checked_at, usage_percent=disk.percent)
        except Exception:
            return self._component("storage", "unknown", checked_at)


class OperationsActivityService:
    """Unified operational activity stream from AuditLog."""

    CATEGORY_MAP = {
        "login_success": "users",
        "login_failed": "users",
        "logout": "users",
        "otp_sent": "users",
        "otp_verified": "users",
        "otp_failed": "users",
        "mfa_required": "users",
        "mfa_completed": "users",
        "session_revoked": "users",
        "token_refresh": "users",
        "election_created": "election",
        "election_updated": "election",
        "election_deleted": "election",
        "election_status_changed": "election",
        "election_accessed": "election",
        "ballot_viewed": "election",
        "ballot_started": "election",
        "ballot_submitted": "election",
        "vote_cast": "election",
        "vote_verified": "election",
        "vote_confirmation_viewed": "election",
        "svt_issued": "strongroom",
        "svt_validated": "strongroom",
        "svt_consumed": "strongroom",
        "svt_revoked": "strongroom",
        "svt_reissued": "strongroom",
        "svt_vote_verified": "strongroom",
        "admin_action": "system",
    }

    def list_activity(
        self,
        *,
        category: str | None = None,
        search: str | None = None,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        logs = audit_log_service.list_logs(hours=hours)
        items = []
        for log in logs:
            cat = self.CATEGORY_MAP.get(log.event_type, "system")
            if category and cat != category:
                continue
            title = log.get_event_type_display() if hasattr(log, "get_event_type_display") else log.event_type
            description = self._describe(log)
            if search:
                haystack = f"{title} {description} {log.event_type}".lower()
                if search.lower() not in haystack:
                    continue
            items.append(
                {
                    "id": str(log.audit_id),
                    "event_type": log.event_type,
                    "category": cat,
                    "title": title,
                    "description": description,
                    "user_email": log.user.email if log.user else None,
                    "election_title": log.election.title if log.election else None,
                    "timestamp": log.timestamp.isoformat(),
                }
            )

        total = len(items)
        page = items[offset : offset + limit]
        return {"items": page, "total": total, "limit": limit, "offset": offset}

    def _describe(self, log) -> str:
        parts = []
        if log.user:
            parts.append(log.user.get_full_name() or log.user.email)
        if log.election:
            parts.append(log.election.title)
        if log.metadata:
            parts.append(str(log.metadata.get("source", "")))
        return " · ".join(p for p in parts if p) or "Operational event recorded"


class OperationsPerformanceService:
    """Operational performance metrics — cached aggregates."""

    def get_metrics(self) -> dict:
        cached = cache.get(PERFORMANCE_CACHE_KEY)
        if cached:
            return cached

        since = timezone.now() - timedelta(hours=24)
        audit_total = audit_log_service.get_summary().get("total_24h", 0)
        vote_throughput = OperationsRepository().recent_votes_count(hours=24)
        comms = communication_service.get_dashboard()
        ussd = USSDSessionRepository().dashboard_stats()

        health = operations_health_service.check_all()
        db_ms = next(
            (c.get("response_time_ms") for c in health["components"] if c["name"] == "database"),
            None,
        )

        payload = {
            "api_response_time_ms": db_ms,
            "authentication_requests_24h": self._count_auth_events(since),
            "vote_throughput_24h": vote_throughput,
            "ussd_requests_24h": ussd.get("requests_today", 0),
            "sms_throughput_24h": comms.get("sms_delivered", 0),
            "email_throughput_24h": comms.get("email_delivered", 0),
            "websocket_messages_estimate_24h": audit_total,
            "cpu_usage_percent": self._component_usage(health, "cpu"),
            "memory_usage_percent": self._component_usage(health, "memory"),
            "disk_usage_percent": self._component_usage(health, "storage"),
            "trends": self._build_trends(),
        }
        cache.set(PERFORMANCE_CACHE_KEY, payload, CACHE_TTL)
        return payload

    def _count_auth_events(self, since) -> int:
        from apps.security.models import AuditLog

        auth_types = {
            AuditLog.EventType.LOGIN_SUCCESS,
            AuditLog.EventType.LOGIN_FAILED,
            AuditLog.EventType.OTP_VERIFIED,
            AuditLog.EventType.MFA_COMPLETED,
        }
        return AuditLog.objects.filter(timestamp__gte=since, event_type__in=auth_types).count()

    def _component_usage(self, health: dict, name: str):
        for component in health.get("components", []):
            if component["name"] == name:
                return component.get("usage_percent")
        return None

    def _build_trends(self) -> dict:
        hours = []
        now = timezone.now()
        repo = OperationsRepository()
        for i in range(6, -1, -1):
            point_time = now - timedelta(hours=i)
            hours.append(
                {
                    "label": point_time.strftime("%H:00"),
                    "votes": max(0, repo.recent_votes_count(hours=1)),
                }
            )
        return {"vote_throughput_hourly": hours}


class OperationsDashboardService:
    """Composed EOC dashboard — reuses existing domain services."""

    def __init__(
        self,
        repository: OperationsRepository | None = None,
        health_service: OperationsHealthService | None = None,
    ):
        self.repository = repository or OperationsRepository()
        self.health_service = health_service or OperationsHealthService()

    def get_overview(self) -> dict:
        cached = cache.get(OVERVIEW_CACHE_KEY)
        if cached:
            return cached

        admin = dashboard_service.get_admin_overview()
        election_counts = self.repository.election_counts()
        sessions = self.repository.session_stats()
        pending = self.repository.pending_workloads()
        comms = communication_service.get_dashboard()
        ussd = USSDSessionRepository().dashboard_stats()
        health = self.health_service.check_all()
        performance = operations_performance_service.get_metrics()

        payload = {
            "system_health": {
                "status": health["overall_status"],
                "checked_at": health["checked_at"],
            },
            "elections": {
                **election_counts,
                "active_total": election_counts["open"] + election_counts["paused"],
                "current_active": election_counts["open"],
            },
            "realtime": {
                "connected_users_estimate": self.repository.online_users_estimate(),
                "authenticated_sessions": sessions["authenticated_sessions"],
                "websocket_status": health["overall_status"],
            },
            "sessions_by_role": {
                "students": sessions["students_online"],
                "candidates": sessions["candidates_online"],
                "admins": sessions["admins_online"],
                "super_admins": sessions["super_admins_online"],
            },
            "pending_workloads": pending,
            "security_summary": admin.get("security_alerts", {}),
            "fraud_summary": admin.get("fraud_cases", {}),
            "communications_summary": {
                "pending_queue": comms.get("pending_queue", 0),
                "retry_queue": comms.get("retry_queue", 0),
                "failed_messages": comms.get("failed_messages", 0),
                "sms_delivered": comms.get("sms_delivered", 0),
                "email_delivered": comms.get("email_delivered", 0),
            },
            "ussd_summary": ussd,
            "performance": {
                "api_response_time_ms": performance.get("api_response_time_ms"),
                "vote_throughput_24h": performance.get("vote_throughput_24h"),
            },
            "resource_usage": {
                "cpu_percent": performance.get("cpu_usage_percent"),
                "memory_percent": performance.get("memory_usage_percent"),
                "disk_percent": performance.get("disk_usage_percent"),
            },
        }
        cache.set(OVERVIEW_CACHE_KEY, payload, CACHE_TTL)
        return payload

    def get_election_monitor(self) -> list[dict]:
        rows = []
        for election in self.repository.active_elections():
            snapshot = dashboard_service.get_election_monitoring(election.uuid)
            if not snapshot:
                continue
            if election.status == Election.Status.OPEN:
                snapshot = sanitize_payload(snapshot, election.status)
                snapshot.pop("total_votes_cast", None)
            snapshot["voting_channels"] = {
                "web": election.allow_web_voting,
                "ussd": election.allow_ussd_voting,
            }
            snapshot["last_activity"] = election.updated_at.isoformat()
            rows.append(snapshot)
        return rows

    def get_infrastructure(self) -> dict:
        health = self.health_service.check_all()
        return {
            "nodes": [
                {"id": "frontend", "label": "Vue Frontend", "status": "healthy", "layer": "client"},
                {"id": "api", "label": "Django API", "status": health["overall_status"], "layer": "application"},
                {"id": "redis", "label": "Redis", "status": self._component_status(health, "redis"), "layer": "cache"},
                {"id": "postgres", "label": "PostgreSQL", "status": self._component_status(health, "database"), "layer": "data"},
                {"id": "channels", "label": "Django Channels", "status": self._component_status(health, "websockets"), "layer": "realtime"},
                {"id": "sms", "label": "SMS Gateway", "status": self._component_status(health, "communications"), "layer": "integration"},
                {"id": "ussd", "label": "USSD Gateway", "status": self._component_status(health, "ussd"), "layer": "integration"},
                {"id": "strongroom", "label": "Strongroom", "status": "healthy", "layer": "integrity"},
                {"id": "results", "label": "Results Engine", "status": "healthy", "layer": "integrity"},
            ],
            "links": [
                {"from": "frontend", "to": "api"},
                {"from": "api", "to": "postgres"},
                {"from": "api", "to": "redis"},
                {"from": "api", "to": "channels"},
                {"from": "api", "to": "sms"},
                {"from": "api", "to": "ussd"},
                {"from": "api", "to": "strongroom"},
                {"from": "api", "to": "results"},
                {"from": "channels", "to": "redis"},
            ],
            "checked_at": health["checked_at"],
        }

    def get_queues(self) -> dict:
        comms = communication_service.get_dashboard()
        ussd = USSDSessionRepository().dashboard_stats()
        return {
            "notification_queue": {
                "pending": comms.get("pending_queue", 0),
                "retry": comms.get("retry_queue", 0),
                "failed": comms.get("failed_messages", 0),
            },
            "sms_queue": {"delivered": comms.get("sms_delivered", 0), "failed": comms.get("failed_messages", 0)},
            "email_queue": {"delivered": comms.get("email_delivered", 0), "failed": comms.get("failed_messages", 0)},
            "ussd_queue": {
                "active": ussd.get("active_sessions", 0),
                "completed": ussd.get("completed_votes", 0),
                "failed": ussd.get("failed_sessions", 0),
            },
            "worker_status": self.health_service._check_workers(timezone.now().isoformat()),
        }

    def get_sessions_detail(self) -> dict:
        stats = self.repository.session_stats()
        from apps.accounts.models import Session

        now = timezone.now()
        recent = (
            Session.objects.filter(is_active=True)
            .select_related("user", "user__role")
            .order_by("-last_activity_at")[:50]
        )
        return {
            **stats,
            "recent_sessions": [
                {
                    "uuid": str(s.uuid),
                    "user_name": s.user.get_full_name() or s.user.email,
                    "role": s.user.role.name if s.user.role else None,
                    "ip_address": s.ip_address,
                    "last_activity_at": s.last_activity_at.isoformat(),
                    "expires_at": s.expires_at.isoformat(),
                }
                for s in recent
            ],
        }

    def get_communications_detail(self) -> dict:
        return communication_service.get_dashboard()

    def get_results_queues(self) -> dict:
        repo = ElectionResultRepository()
        return {
            "certification_pending": repo.list_certification_queue().count(),
            "publication_pending": repo.list_publication_queue().count(),
        }

    def _component_status(self, health: dict, name: str) -> str:
        for component in health.get("components", []):
            if component["name"] == name:
                return component.get("status", "unknown")
        return "unknown"


operations_health_service = OperationsHealthService()
operations_activity_service = OperationsActivityService()
operations_performance_service = OperationsPerformanceService()
operations_dashboard_service = OperationsDashboardService()
