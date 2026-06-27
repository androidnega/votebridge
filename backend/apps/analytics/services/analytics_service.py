import csv
import io
import logging
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from apps.accounts.models import Role
from apps.dashboard.services.dashboard_service import dashboard_service
from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from apps.fraud.services.alert_service import (
    audit_log_service,
    device_monitoring_service,
    location_monitoring_service,
    security_alert_service,
)
from apps.fraud.services.fraud_case_service import fraud_case_service
from apps.notifications.services.communication_service import communication_service
from apps.operations.repositories.operations_repository import OperationsRepository
from apps.operations.services.operations_service import (
    operations_dashboard_service,
    operations_health_service,
    operations_performance_service,
)
from apps.results.repositories.election_result_repository import ElectionResultRepository
from apps.results.services.certification_service import certification_service
from apps.results.services.report_service import report_service
from apps.security.models import AuditLog
from apps.security.repositories.monitoring_repository import AuditLogRepository
from apps.strongroom.services.integrity_verification_service import integrity_verification_service
from apps.ussd.repositories.ussd_repository import USSDSessionRepository
from apps.analytics.repositories.analytics_repository import AnalyticsRepository
from core.realtime.sanitize import sanitize_payload

logger = logging.getLogger("votebridge")

CACHE_TTL = 60
OVERVIEW_CACHE = "analytics:overview"


class AnalyticsDashboardService:
    """Enterprise ABI overview — composes existing domain services."""

    def __init__(self, repository: AnalyticsRepository | None = None):
        self.repository = repository or AnalyticsRepository()
        self.operations_repo = OperationsRepository()

    def get_overview(self) -> dict:
        cached = cache.get(OVERVIEW_CACHE)
        if cached:
            return cached

        admin = dashboard_service.get_admin_overview()
        performance = operations_performance_service.get_metrics()
        comms = communication_service.get_dashboard()
        ussd = USSDSessionRepository().dashboard_stats()
        fraud = fraud_case_service.get_integrity_report()
        security = security_alert_service.get_summary()
        election_counts = self.operations_repo.election_counts()

        completed = self.repository.completed_elections_count()
        comparisons = self.repository.election_comparison(limit=10)
        avg_turnout = (
            round(sum(e["turnout_percent"] for e in comparisons) / len(comparisons), 1)
            if comparisons
            else 0.0
        )

        hourly_votes = self.repository.vote_hourly_buckets(24)
        peak_voting = max(hourly_votes, key=lambda x: x["value"], default={"label": "—", "value": 0})

        auth_events = AuditLogRepository().count_events(
            AuditLog.EventType.LOGIN_SUCCESS,
            since=timezone.now() - timedelta(hours=24),
        )
        auth_hourly = self._auth_hourly_buckets()
        peak_auth = max(auth_hourly, key=lambda x: x["value"], default={"label": "—", "value": 0})

        sms_total = comms.get("sms_delivered", 0) + comms.get("failed_messages", 0)
        sms_success = (
            round((comms.get("sms_delivered", 0) / sms_total) * 100, 1) if sms_total else 0.0
        )

        payload = {
            "overall_participation_percent": admin.get("turnout_percentage", 0),
            "overall_turnout_percent": admin.get("turnout_percentage", 0),
            "completed_elections": completed,
            "average_turnout_percent": avg_turnout,
            "average_voting_duration_minutes": None,
            "average_session_duration_minutes": None,
            "peak_voting_hour": peak_voting.get("label"),
            "peak_authentication_hour": peak_auth.get("label"),
            "total_votes": admin.get("total_votes_cast", 0),
            "total_students": self.repository.total_students(),
            "total_active_voters": admin.get("registered_voters", 0),
            "total_fraud_cases": fraud.get("total_fraud_cases", 0),
            "total_security_alerts": security.get("open", 0) + security.get("escalated", 0),
            "average_integrity_score": None,
            "average_api_response_time_ms": performance.get("api_response_time_ms"),
            "average_websocket_latency_ms": performance.get("api_response_time_ms"),
            "average_sms_delivery_success_percent": sms_success,
            "average_ussd_usage": ussd.get("requests_today", 0),
            "system_utilization": {
                "cpu_percent": performance.get("cpu_usage_percent"),
                "memory_percent": performance.get("memory_usage_percent"),
                "disk_percent": performance.get("disk_usage_percent"),
            },
            "election_status": election_counts,
            "operations_health": {"status": "healthy" if performance.get("api_response_time_ms") is not None else "unknown"},
            "trends": {
                "votes_hourly": hourly_votes,
                "auth_hourly": auth_hourly,
            },
        }
        cache.set(OVERVIEW_CACHE, payload, CACHE_TTL)
        return payload

    def _auth_hourly_buckets(self) -> list[dict]:
        since = timezone.now() - timedelta(hours=24)
        rows = (
            AuditLog.objects.filter(
                timestamp__gte=since,
                event_type__in=[
                    AuditLog.EventType.LOGIN_SUCCESS,
                    AuditLog.EventType.OTP_VERIFIED,
                ],
            )
            .annotate(bucket=TruncHour("timestamp"))
            .values("bucket")
            .annotate(count=Count("audit_id"))
            .order_by("bucket")
        )
        return [{"label": row["bucket"].strftime("%H:00"), "value": row["count"]} for row in rows]


class AnalyticsElectionService:
    def __init__(self, repository: AnalyticsRepository | None = None):
        self.repository = repository or AnalyticsRepository()
        self.election_repository = ElectionRepository()

    def list_elections(self) -> list[dict]:
        return self.repository.election_comparison(limit=50)

    def get_election(self, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return {}
        snapshot = dashboard_service.get_election_monitoring(election_uuid)
        if election.status == Election.Status.OPEN:
            snapshot = sanitize_payload(snapshot, election.status)
            snapshot.pop("total_votes_cast", None)
        snapshot["channels"] = self.repository.channel_breakdown(election)
        snapshot["voting_channels"] = {
            "web": election.allow_web_voting,
            "ussd": election.allow_ussd_voting,
        }
        return snapshot

    def compare_elections(self) -> dict:
        rows = self.repository.election_comparison(limit=10)
        most_active = sorted(rows, key=lambda r: r.get("turnout_percent", 0), reverse=True)[:5]
        least_active = sorted(rows, key=lambda r: r.get("turnout_percent", 0))[:5]
        return {
            "comparison": rows,
            "most_active": most_active,
            "least_active": least_active,
            "trend": self.repository.vote_daily_buckets(30),
        }


class AnalyticsParticipationService:
    def __init__(self, repository: AnalyticsRepository | None = None):
        self.repository = repository or AnalyticsRepository()

    def get_participation(self) -> dict:
        breakdown = self.repository.participation_breakdown()
        admin = dashboard_service.get_admin_overview()
        return {
            **breakdown,
            "registered_voters": admin.get("registered_voters", 0),
            "actual_turnout": admin.get("turnout_percentage", 0),
            "heatmap": [
                {"x": p["label"], "y": p["faculty"], "value": p["turnout_percent"]}
                for p in breakdown["programmes"]
            ],
        }

    def get_departments(self) -> list[dict]:
        return self.repository.participation_breakdown()["departments"]

    def get_faculties(self) -> list[dict]:
        return self.repository.participation_breakdown()["faculties"]

    def get_programmes(self) -> list[dict]:
        return self.repository.participation_breakdown()["programmes"]


class AnalyticsStudentService:
    def get_student_analytics(self) -> dict:
        device = device_monitoring_service.get_summary()
        audit = audit_log_service.get_summary()
        return {
            "login_trends": self._event_trend(AuditLog.EventType.LOGIN_SUCCESS),
            "voting_trends": self._event_trend(AuditLog.EventType.VOTE_CAST),
            "device_types": device.get("by_device_type", []),
            "operating_systems": [],
            "browser_usage": [],
            "audit_summary": audit,
        }

    def get_personal_analytics(self, user) -> dict:
        overview = dashboard_service.get_student_overview(user)
        my_votes = audit_log_service.list_logs(user_uuid=str(user.uuid), hours=24 * 90)
        vote_events = [log for log in my_votes if log.event_type == AuditLog.EventType.VOTE_CAST]
        return {
            "active_elections": overview.get("active_elections_count", 0),
            "votes_cast": len(vote_events),
            "election_status_summary": overview.get("election_status_summary", {}),
            "note": "Personal analytics only — no institutional standings exposed.",
        }

    def _event_trend(self, event_type: str) -> list[dict]:
        since = timezone.now() - timedelta(days=14)
        rows = (
            AuditLog.objects.filter(event_type=event_type, timestamp__gte=since)
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(count=Count("audit_id"))
            .order_by("day")
        )
        return [{"label": str(row["day"]), "value": row["count"]} for row in rows]


class AnalyticsSecurityService:
    def get_security_analytics(self) -> dict:
        audit = audit_log_service.get_summary()
        alerts = security_alert_service.get_summary()
        devices = device_monitoring_service.get_summary()
        locations = location_monitoring_service.get_summary()
        failed = AuditLogRepository().count_events(
            AuditLog.EventType.LOGIN_FAILED,
            since=timezone.now() - timedelta(days=7),
        )
        success = AuditLogRepository().count_events(
            AuditLog.EventType.LOGIN_SUCCESS,
            since=timezone.now() - timedelta(days=7),
        )
        return {
            "failed_logins_7d": failed,
            "successful_logins_7d": success,
            "otp_requests_7d": AuditLogRepository().count_events(
                AuditLog.EventType.OTP_SENT,
                since=timezone.now() - timedelta(days=7),
            ),
            "security_alerts": alerts,
            "device_trends": devices,
            "location_trends": locations,
            "audit_summary": audit,
            "alerts_over_time": self._alert_trend(),
        }

    def _alert_trend(self) -> list[dict]:
        from apps.fraud.models import SecurityAlert

        since = timezone.now() - timedelta(days=30)
        rows = (
            SecurityAlert.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("alert_id"))
            .order_by("day")
        )
        return [{"label": str(row["day"]), "value": row["count"]} for row in rows]


class AnalyticsFraudService:
    def get_fraud_analytics(self) -> dict:
        from apps.fraud.repositories.fraud_case_repository import FraudCaseRepository

        report = fraud_case_service.get_integrity_report()
        repo = FraudCaseRepository()
        by_type = list(repo.count_by_severity())
        by_status = list(repo.count_by_status())
        cases = fraud_case_service.list_cases()
        by_election: dict[str, int] = {}
        for case in cases[:500]:
            key = case.election.title if case.election else "Platform"
            by_election[key] = by_election.get(key, 0) + 1
        return {
            "integrity_report": report,
            "risk_distribution": by_type,
            "cases_by_type": [{"type": row["severity"], "count": row["count"]} for row in by_type],
            "cases_by_election": [{"election": k, "count": v} for k, v in by_election.items()],
            "investigation_status": by_status,
        }


class AnalyticsOperationsService:
    def get_operations_analytics(self) -> dict:
        health = operations_health_service.check_all()
        performance = operations_performance_service.get_metrics()
        overview = operations_dashboard_service.get_overview()
        return {
            "api_performance": performance,
            "queue_performance": overview.get("communications_summary"),
            "health_components": health.get("components", []),
            "websocket_status": overview.get("realtime", {}),
            "cpu_trend": performance.get("trends", {}).get("vote_throughput_hourly", []),
            "memory_percent": performance.get("memory_usage_percent"),
            "storage_percent": performance.get("disk_usage_percent"),
        }


class AnalyticsCommunicationService:
    def get_communication_analytics(self) -> dict:
        dashboard = communication_service.get_dashboard()
        return {
            "sms_sent": dashboard.get("sms_delivered", 0) + dashboard.get("failed_messages", 0),
            "sms_delivered": dashboard.get("sms_delivered", 0),
            "sms_failed": dashboard.get("failed_messages", 0),
            "email_delivered": dashboard.get("email_delivered", 0),
            "pending_queue": dashboard.get("pending_queue", 0),
            "retry_queue": dashboard.get("retry_queue", 0),
            "providers": dashboard.get("providers", []),
            "delivery_success_rate": self._success_rate(dashboard),
        }

    def _success_rate(self, dashboard: dict) -> float:
        delivered = dashboard.get("sms_delivered", 0) + dashboard.get("email_delivered", 0)
        failed = dashboard.get("failed_messages", 0)
        total = delivered + failed
        return round((delivered / total) * 100, 1) if total else 0.0


class AnalyticsUssdService:
    def get_ussd_analytics(self) -> dict:
        stats = USSDSessionRepository().dashboard_stats()
        return {
            **stats,
            "sessions_total": stats.get("active_sessions", 0) + stats.get("completed_votes", 0),
            "abandoned_sessions": stats.get("failed_sessions", 0),
            "voting_completion_rate": self._completion_rate(stats),
        }

    def _completion_rate(self, stats: dict) -> float:
        completed = stats.get("completed_votes", 0)
        failed = stats.get("failed_sessions", 0)
        total = completed + failed
        return round((completed / total) * 100, 1) if total else 0.0


class AnalyticsStrongroomService:
    def get_strongroom_analytics(self) -> dict:
        elections = Election.objects.filter(
            status__in=[Election.Status.CLOSED, Election.Status.ARCHIVED]
        ).order_by("-start_date")[:5]
        dashboards = []
        scores = []
        for election in elections:
            data = integrity_verification_service.get_dashboard(election.uuid)
            if data:
                dashboards.append(data)
                if data.get("integrity_score") is not None:
                    scores.append(data["integrity_score"])
        avg_score = round(sum(scores) / len(scores), 1) if scores else None
        return {
            "average_integrity_score": avg_score,
            "election_dashboards": dashboards,
            "verification_trends": [{"label": d.get("election_title"), "value": d.get("integrity_score")} for d in dashboards],
        }


class AnalyticsHistoricalService:
    def __init__(self, repository: AnalyticsRepository | None = None):
        self.repository = repository or AnalyticsRepository()

    def get_trends(self, period: str) -> dict:
        if period == "daily":
            points = self.repository.vote_daily_buckets(30)
        elif period == "weekly":
            points = self.repository.vote_daily_buckets(90)
        elif period == "monthly":
            points = self.repository.vote_daily_buckets(365)
        else:
            points = self.repository.vote_daily_buckets(180)
        return {
            "period": period,
            "vote_trends": points,
            "election_comparison": self.repository.election_comparison(10),
            "institution_comparison": [],
        }


class AnalyticsReportService:
    """Export analytics reports — reuses results report_service for certified election data."""

    def __init__(self):
        self.dashboard = AnalyticsDashboardService()
        self.participation = AnalyticsParticipationService()
        self.security = AnalyticsSecurityService()
        self.fraud = AnalyticsFraudService()
        self.operations = AnalyticsOperationsService()
        self.communication = AnalyticsCommunicationService()
        self.strongroom = AnalyticsStrongroomService()

    def generate(self, report_type: str, export_format: str, *, election_uuid=None) -> dict:
        data = self._collect(report_type, election_uuid=election_uuid)
        if export_format == "json":
            return {"format": "json", "content": data, "content_type": "application/json"}
        if export_format == "csv":
            return self._as_csv(report_type, data)
        if export_format in {"excel", "xlsx"}:
            return {
                "format": "excel",
                "content": data,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "note": "Structured rows prepared; binary generation deferred to client.",
            }
        if export_format == "pdf":
            return {
                "format": "pdf",
                "content": data,
                "content_type": "application/pdf",
                "note": "Structured payload prepared; PDF rendering deferred.",
            }
        return {"format": export_format, "content": data}

    def _collect(self, report_type: str, *, election_uuid=None) -> dict:
        if report_type == "election" and election_uuid:
            result = certification_service.get_result_for_election(election_uuid)
            if result and result.status in {"certified", "published", "archived"}:
                return report_service.prepare_csv(result)
        collectors = {
            "election": lambda: AnalyticsElectionService().compare_elections(),
            "participation": self.participation.get_participation,
            "security": self.security.get_security_analytics,
            "fraud": self.fraud.get_fraud_analytics,
            "operations": self.operations.get_operations_analytics,
            "communication": self.communication.get_communication_analytics,
            "strongroom": self.strongroom.get_strongroom_analytics,
            "institution": self.dashboard.get_overview,
        }
        return collectors[report_type]()

    def _as_csv(self, report_type: str, data: dict) -> dict:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["report_type", report_type])
        writer.writerow(["generated_at", timezone.now().isoformat()])
        writer.writerow([])
        self._flatten_to_csv(writer, data)
        return {
            "format": "csv",
            "filename": f"votebridge_{report_type}_analytics.csv",
            "content_type": "text/csv",
            "content": buffer.getvalue(),
        }

    def _flatten_to_csv(self, writer, data, prefix=""):
        if isinstance(data, dict):
            for key, value in data.items():
                self._flatten_to_csv(writer, value, f"{prefix}{key}.")
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                self._flatten_to_csv(writer, item, f"{prefix}{idx}.")
        else:
            writer.writerow([prefix.rstrip("."), data])


analytics_dashboard_service = AnalyticsDashboardService()
analytics_election_service = AnalyticsElectionService()
analytics_participation_service = AnalyticsParticipationService()
analytics_student_service = AnalyticsStudentService()
analytics_security_service = AnalyticsSecurityService()
analytics_fraud_service = AnalyticsFraudService()
analytics_operations_service = AnalyticsOperationsService()
analytics_communication_service = AnalyticsCommunicationService()
analytics_ussd_service = AnalyticsUssdService()
analytics_strongroom_service = AnalyticsStrongroomService()
analytics_historical_service = AnalyticsHistoricalService()
analytics_report_service = AnalyticsReportService()
