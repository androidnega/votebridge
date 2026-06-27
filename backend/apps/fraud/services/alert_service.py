import logging
from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django.utils import timezone

from apps.fraud.models import SecurityAlert
from apps.fraud.repositories.alert_repository import SecurityAlertRepository
from apps.fraud.validators import validate_alert_status_transition
from apps.security.models import AuditLog, DeviceLog, LocationLog
from apps.security.repositories.monitoring_repository import (
    AuditLogRepository,
    DeviceLogRepository,
    LocationLogRepository,
)
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class AuditLogService:
    def __init__(self, repository: AuditLogRepository | None = None):
        self.repository = repository or AuditLogRepository()

    def list_logs(
        self,
        event_type: str | None = None,
        election_uuid: str | None = None,
        user_uuid: str | None = None,
        hours: int | None = None,
    ):
        election_id = None
        user_id = None
        since = None
        if hours:
            since = timezone.now() - timedelta(hours=hours)
        if election_uuid:
            from apps.elections.repositories.election_repository import ElectionRepository
            election = ElectionRepository().get_by_uuid(election_uuid)
            if election:
                election_id = election.id
        if user_uuid:
            from apps.accounts.repositories.user_repository import UserRepository
            user = UserRepository().get_by_uuid(user_uuid)
            if user:
                user_id = user.id
        return self.repository.list_filtered(
            event_type=event_type,
            election_id=election_id,
            user_id=user_id,
            since=since,
        )

    def get_summary(self) -> dict:
        since = timezone.now() - timedelta(hours=24)
        qs = AuditLog.objects.filter(timestamp__gte=since)
        by_type = qs.values("event_type").annotate(count=Count("audit_id")).order_by("-count")
        return {
            "total_24h": qs.count(),
            "by_event_type": list(by_type),
        }


class DeviceMonitoringService:
    def __init__(self, repository: DeviceLogRepository | None = None):
        self.repository = repository or DeviceLogRepository()

    def list_devices(self, device_type: str | None = None):
        qs = self.repository.get_queryset()
        if device_type:
            qs = qs.filter(device_type=device_type)
        return qs

    def get_summary(self) -> dict:
        since = timezone.now() - timedelta(hours=24)
        qs = DeviceLog.objects.filter(last_seen_at__gte=since)
        by_type = qs.values("device_type").annotate(count=Count("device_log_id"))
        return {
            "total_24h": qs.count(),
            "by_device_type": list(by_type),
        }


class LocationMonitoringService:
    def __init__(self, repository: LocationLogRepository | None = None):
        self.repository = repository or LocationLogRepository()

    def list_locations(self, country: str | None = None):
        qs = self.repository.get_queryset()
        if country:
            qs = qs.filter(country__iexact=country)
        return qs

    def get_summary(self) -> dict:
        since = timezone.now() - timedelta(hours=24)
        qs = LocationLog.objects.filter(last_seen_at__gte=since)
        by_country = qs.values("country").annotate(count=Count("location_log_id")).order_by("-count")[:10]
        return {
            "total_24h": qs.count(),
            "by_country": list(by_country),
        }


class SecurityAlertService:
    def __init__(self, repository: SecurityAlertRepository | None = None):
        self.repository = repository or SecurityAlertRepository()

    def list_alerts(
        self,
        status: str | None = None,
        alert_type: str | None = None,
        election_uuid: str | None = None,
    ):
        election_id = None
        if election_uuid:
            from apps.elections.repositories.election_repository import ElectionRepository
            election = ElectionRepository().get_by_uuid(election_uuid)
            if election:
                election_id = election.id
        return self.repository.list_filtered(
            status=status,
            alert_type=alert_type,
            election_id=election_id,
        )

    def get_alert(self, alert_id) -> SecurityAlert:
        alert = self.repository.get_by_alert_id(alert_id)
        if not alert:
            raise NotFoundError(message="Alert not found.", code="alert_not_found")
        return alert

    def review_alert(self, alert_id, admin_user) -> SecurityAlert:
        alert = self.get_alert(alert_id)
        try:
            validate_alert_status_transition(alert.status, SecurityAlert.Status.REVIEWING)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_alert_transition") from exc
        return self.repository.update(
            alert,
            status=SecurityAlert.Status.REVIEWING,
            reviewed_at=timezone.now(),
            reviewed_by=admin_user,
        )

    def resolve_alert(self, alert_id, admin_user) -> SecurityAlert:
        alert = self.get_alert(alert_id)
        if alert.status == SecurityAlert.Status.RESOLVED:
            raise ConflictError(message="Alert is already resolved.", code="alert_already_resolved")
        alert = self.repository.update(
            alert,
            status=SecurityAlert.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolved_by=admin_user,
        )
        self._broadcast_alert_resolved(alert)
        return alert

    def _broadcast_alert_resolved(self, alert: SecurityAlert) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.security_alert_resolved(
                alert,
                admin_stats=dashboard_service.get_admin_overview(),
            )
        except Exception:
            logger.exception("Failed to broadcast security alert resolved %s", alert.alert_id)

    def escalate_alert(self, alert_id, admin_user) -> SecurityAlert:
        alert = self.get_alert(alert_id)
        try:
            validate_alert_status_transition(alert.status, SecurityAlert.Status.ESCALATED)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_alert_transition") from exc
        return self.repository.update(
            alert,
            status=SecurityAlert.Status.ESCALATED,
            escalated_at=timezone.now(),
            escalated_by=admin_user,
        )

    def get_summary(self) -> dict:
        counts = {item["status"]: item["count"] for item in self.repository.count_by_status()}
        return {
            "open": counts.get(SecurityAlert.Status.OPEN, 0),
            "reviewing": counts.get(SecurityAlert.Status.REVIEWING, 0),
            "escalated": counts.get(SecurityAlert.Status.ESCALATED, 0),
            "resolved": counts.get(SecurityAlert.Status.RESOLVED, 0),
        }


audit_log_service = AuditLogService()
device_monitoring_service = DeviceMonitoringService()
location_monitoring_service = LocationMonitoringService()
security_alert_service = SecurityAlertService()
