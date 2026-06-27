import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.fraud.models import SecurityAlert
from apps.fraud.repositories.alert_repository import SecurityAlertRepository
from apps.security.models import AuditLog
from apps.security.repositories.monitoring_repository import AuditLogRepository, DeviceLogRepository

logger = logging.getLogger("votebridge")


class AlertDetectionService:
    """Rule-based alert creation — prepares for fraud detection without scoring."""

    def __init__(
        self,
        alert_repository: SecurityAlertRepository | None = None,
        audit_repository: AuditLogRepository | None = None,
        device_repository: DeviceLogRepository | None = None,
    ):
        self.alert_repository = alert_repository or SecurityAlertRepository()
        self.audit_repository = audit_repository or AuditLogRepository()
        self.device_repository = device_repository or DeviceLogRepository()

    def evaluate(self, audit_log: AuditLog, device_log=None, location_log=None) -> None:
        self._check_excessive_login_attempts(audit_log)
        self._check_excessive_svt_requests(audit_log)
        self._check_suspicious_voting_pattern(audit_log)
        if device_log:
            self._check_multiple_accounts_same_device(audit_log, device_log)
        if location_log and audit_log.user_id:
            self._check_duplicate_location(audit_log, location_log)

    def _window_minutes(self, key: str, default: int) -> int:
        return int(getattr(settings, key, default))

    def _create_alert(
        self,
        alert_type: str,
        title: str,
        description: str,
        user=None,
        election=None,
        device_log=None,
        location_log=None,
        metadata=None,
    ) -> SecurityAlert | None:
        if self.alert_repository.has_open_alert(
            alert_type=alert_type,
            user_id=user.id if user else None,
            election_id=election.id if election else None,
        ):
            return None
        alert = self.alert_repository.create(
            alert_type=alert_type,
            status=SecurityAlert.Status.OPEN,
            user=user,
            election=election,
            device_log=device_log,
            location_log=location_log,
            title=title,
            description=description,
            metadata=metadata or {},
        )
        logger.warning("Security alert created: %s (%s)", alert_type, alert.alert_id)
        self._create_fraud_case_from_alert(alert)
        self._broadcast_alert_created(alert)
        return alert

    def _broadcast_alert_created(self, alert: SecurityAlert) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.security_alert_created(
                alert,
                admin_stats=dashboard_service.get_admin_overview(),
            )
        except Exception:
            logger.exception("Failed to broadcast security alert created %s", alert.alert_id)

    def _create_fraud_case_from_alert(self, alert: SecurityAlert) -> None:
        try:
            from apps.fraud.services.fraud_case_service import fraud_case_service

            fraud_case_service.create_from_alert(alert)
        except Exception:
            logger.exception("Failed to create fraud case for alert %s", alert.alert_id)

    def _check_excessive_login_attempts(self, audit_log: AuditLog) -> None:
        if audit_log.event_type != AuditLog.EventType.LOGIN_FAILED:
            return
        window = self._window_minutes("ALERT_LOGIN_ATTEMPTS_WINDOW_MINUTES", 15)
        threshold = self._window_minutes("ALERT_LOGIN_ATTEMPTS_THRESHOLD", 5)
        since = timezone.now() - timedelta(minutes=window)
        count = self.audit_repository.count_events(
            AuditLog.EventType.LOGIN_FAILED,
            since=since,
            ip_address=audit_log.ip_address,
        )
        if count >= threshold:
            self._create_alert(
                SecurityAlert.AlertType.EXCESSIVE_LOGIN_ATTEMPTS,
                "Excessive login attempts detected",
                f"{count} failed login attempts from IP {audit_log.ip_address} in {window} minutes.",
                user=audit_log.user,
                location_log=audit_log.location_log,
                metadata={"ip_address": audit_log.ip_address, "attempt_count": count},
            )

    def _check_excessive_svt_requests(self, audit_log: AuditLog) -> None:
        if audit_log.event_type != AuditLog.EventType.SVT_ISSUED:
            return
        window = self._window_minutes("ALERT_SVT_REQUESTS_WINDOW_MINUTES", 60)
        threshold = self._window_minutes("ALERT_SVT_REQUESTS_THRESHOLD", 5)
        since = timezone.now() - timedelta(minutes=window)
        count = self.audit_repository.count_events(
            AuditLog.EventType.SVT_ISSUED,
            since=since,
            user_id=audit_log.user_id,
        )
        if count >= threshold:
            self._create_alert(
                SecurityAlert.AlertType.EXCESSIVE_SVT_REQUESTS,
                "Excessive SVT requests",
                f"User requested {count} SVT tokens in {window} minutes.",
                user=audit_log.user,
                election=audit_log.election,
                metadata={"request_count": count},
            )

    def _check_suspicious_voting_pattern(self, audit_log: AuditLog) -> None:
        if audit_log.event_type != AuditLog.EventType.BALLOT_SUBMITTED:
            return
        window = self._window_minutes("ALERT_VOTING_PATTERN_WINDOW_MINUTES", 5)
        threshold = self._window_minutes("ALERT_VOTING_PATTERN_THRESHOLD", 2)
        since = timezone.now() - timedelta(minutes=window)
        count = self.audit_repository.count_events(
            AuditLog.EventType.BALLOT_SUBMITTED,
            since=since,
            user_id=audit_log.user_id,
        )
        if count >= threshold:
            self._create_alert(
                SecurityAlert.AlertType.SUSPICIOUS_VOTING_PATTERN,
                "Suspicious voting pattern",
                f"User submitted {count} ballots within {window} minutes.",
                user=audit_log.user,
                election=audit_log.election,
                metadata={"ballot_count": count},
            )

    def _check_multiple_accounts_same_device(self, audit_log: AuditLog, device_log) -> None:
        window = self._window_minutes("ALERT_DEVICE_WINDOW_MINUTES", 1440)
        since = timezone.now() - timedelta(minutes=window)
        user_count = self.device_repository.count_users_for_fingerprint(
            device_log.browser_fingerprint,
            since=since,
        )
        if user_count >= 2:
            self._create_alert(
                SecurityAlert.AlertType.MULTIPLE_ACCOUNTS_SAME_DEVICE,
                "Multiple accounts on same device",
                f"{user_count} distinct accounts seen on the same device fingerprint.",
                user=audit_log.user,
                device_log=device_log,
                metadata={"fingerprint": device_log.browser_fingerprint, "account_count": user_count},
            )
            self._create_alert(
                SecurityAlert.AlertType.DUPLICATE_DEVICE,
                "Duplicate device detected",
                f"Device fingerprint shared across {user_count} accounts.",
                user=audit_log.user,
                device_log=device_log,
                metadata={"fingerprint": device_log.browser_fingerprint, "account_count": user_count},
            )

    def _check_duplicate_location(self, audit_log: AuditLog, location_log) -> None:
        if audit_log.event_type not in {
            AuditLog.EventType.VOTE_CAST,
            AuditLog.EventType.BALLOT_SUBMITTED,
            AuditLog.EventType.SVT_ISSUED,
            AuditLog.EventType.SVT_VALIDATED,
        }:
            return
        window = self._window_minutes("ALERT_LOCATION_WINDOW_MINUTES", 60)
        since = timezone.now() - timedelta(minutes=window)
        from apps.security.repositories.monitoring_repository import LocationLogRepository

        repo = LocationLogRepository()
        user_count = repo.count_users_for_ip(location_log.ip_address, since=since)
        if user_count >= 2:
            self._create_alert(
                SecurityAlert.AlertType.DUPLICATE_LOCATION,
                "Duplicate location detected",
                f"IP {location_log.ip_address} used by {user_count} accounts for voting activity.",
                user=audit_log.user,
                election=audit_log.election,
                location_log=location_log,
                metadata={"ip_address": location_log.ip_address, "account_count": user_count},
            )
