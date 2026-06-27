import logging
from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.fraud.models import FraudCase, SecurityAlert
from apps.fraud.repositories.fraud_case_repository import FraudCaseRepository
from apps.fraud.services.risk_scoring_service import (
    calculate_risk_score_for_alert,
    severity_from_score,
)
from apps.fraud.validators import (
    validate_fraud_case_status_transition,
    validate_investigation_note,
)
from apps.security.models import AuditLog
from apps.security.repositories.monitoring_repository import AuditLogRepository
from apps.voting.repositories.vote_repository import VoteRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class FraudCaseService:
    """Fraud case creation, risk scoring, and investigation workflow."""

    def __init__(
        self,
        case_repository: FraudCaseRepository | None = None,
        audit_repository: AuditLogRepository | None = None,
        vote_repository: VoteRepository | None = None,
    ):
        self.case_repository = case_repository or FraudCaseRepository()
        self.audit_repository = audit_repository or AuditLogRepository()
        self.vote_repository = vote_repository or VoteRepository()

    @transaction.atomic
    def create_from_alert(self, alert: SecurityAlert) -> FraudCase | None:
        if self.case_repository.get_by_alert_id(alert.alert_id):
            return None

        risk_score = calculate_risk_score_for_alert(alert.alert_type)
        severity = severity_from_score(risk_score)

        case = self.case_repository.create(
            election=alert.election,
            user=alert.user,
            related_alert=alert,
            risk_score=risk_score,
            severity=severity,
            status=FraudCase.Status.OPEN,
            investigation_notes=self._format_note(
                "system",
                f"Fraud case opened from alert: {alert.title} ({alert.alert_type}).",
            ),
        )
        logger.warning(
            "Fraud case created: %s (score=%s, severity=%s)",
            case.fraud_case_id,
            risk_score,
            severity,
        )
        self._broadcast_case_created(case)
        return case

    def _broadcast_case_created(self, case: FraudCase) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.fraud_case_created(
                case,
                fraud_stats=dashboard_service.get_fraud_feed_snapshot()["summary"],
            )
        except Exception:
            logger.exception("Failed to broadcast fraud case created %s", case.fraud_case_id)

    def get_case(self, fraud_case_id) -> FraudCase:
        case = self.case_repository.get_by_fraud_case_id(fraud_case_id)
        if not case:
            raise NotFoundError(message="Fraud case not found.", code="fraud_case_not_found")
        return case

    def list_cases(
        self,
        status: str | None = None,
        severity: str | None = None,
        election_uuid: str | None = None,
    ):
        election_id = None
        if election_uuid:
            from apps.elections.repositories.election_repository import ElectionRepository
            election = ElectionRepository().get_by_uuid(election_uuid)
            if election:
                election_id = election.id
        return self.case_repository.list_filtered(
            status=status,
            severity=severity,
            election_id=election_id,
        )

    def get_integrity_report(self, election_uuid: str | None = None) -> dict:
        if election_uuid:
            from apps.elections.repositories.election_repository import ElectionRepository
            election = ElectionRepository().get_by_uuid(election_uuid)
            if not election:
                raise NotFoundError(message="Election not found.", code="election_not_found")
            qs = self.case_repository.list_filtered(election_id=election.id)
            total = qs.count()
            open_cases = qs.filter(
                status__in=[
                    FraudCase.Status.OPEN,
                    FraudCase.Status.INVESTIGATING,
                    FraudCase.Status.ESCALATED,
                ]
            ).count()
            resolved_cases = qs.filter(
                status__in=[FraudCase.Status.RESOLVED, FraudCase.Status.DISMISSED]
            ).count()
            high_risk = qs.filter(severity=FraudCase.Severity.HIGH).count()
            critical = qs.filter(severity=FraudCase.Severity.CRITICAL).count()
            return {
                "total_fraud_cases": total,
                "open_cases": open_cases,
                "resolved_cases": resolved_cases,
                "high_risk_cases": high_risk,
                "critical_cases": critical,
                "election_uuid": str(election.uuid),
            }
        return self.case_repository.get_integrity_counts()

    @transaction.atomic
    def start_investigation(self, fraud_case_id, admin_user) -> FraudCase:
        case = self.get_case(fraud_case_id)
        try:
            validate_fraud_case_status_transition(case.status, FraudCase.Status.INVESTIGATING)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_case_transition") from exc

        notes = self._append_note(
            case.investigation_notes,
            admin_user,
            "Investigation started.",
        )
        return self.case_repository.update(
            case,
            status=FraudCase.Status.INVESTIGATING,
            investigation_notes=notes,
        )

    @transaction.atomic
    def add_investigation_note(self, fraud_case_id, admin_user, note: str) -> FraudCase:
        case = self.get_case(fraud_case_id)
        try:
            validate_investigation_note(note)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="invalid_note") from exc

        notes = self._append_note(case.investigation_notes, admin_user, note.strip())
        return self.case_repository.update(case, investigation_notes=notes)

    @transaction.atomic
    def resolve_case(self, fraud_case_id, admin_user, note: str = "") -> FraudCase:
        case = self.get_case(fraud_case_id)
        if case.status in {FraudCase.Status.RESOLVED, FraudCase.Status.DISMISSED}:
            raise ConflictError(message="Case is already closed.", code="case_already_closed")

        notes = case.investigation_notes
        if note:
            notes = self._append_note(notes, admin_user, note.strip())
        notes = self._append_note(notes, admin_user, "Case resolved.")

        case = self.case_repository.update(
            case,
            status=FraudCase.Status.RESOLVED,
            investigation_notes=notes,
        )
        self._broadcast_case_resolved(case)
        return case

    @transaction.atomic
    def dismiss_case(self, fraud_case_id, admin_user, note: str = "") -> FraudCase:
        case = self.get_case(fraud_case_id)
        if case.status in {FraudCase.Status.RESOLVED, FraudCase.Status.DISMISSED}:
            raise ConflictError(message="Case is already closed.", code="case_already_closed")

        notes = case.investigation_notes
        if note:
            notes = self._append_note(notes, admin_user, note.strip())
        notes = self._append_note(notes, admin_user, "Case dismissed as false positive.")

        case = self.case_repository.update(
            case,
            status=FraudCase.Status.DISMISSED,
            investigation_notes=notes,
        )
        self._broadcast_case_resolved(case)
        return case

    @transaction.atomic
    def escalate_case(self, fraud_case_id, admin_user, note: str = "") -> FraudCase:
        case = self.get_case(fraud_case_id)
        try:
            validate_fraud_case_status_transition(case.status, FraudCase.Status.ESCALATED)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc), code="invalid_case_transition") from exc

        notes = case.investigation_notes
        if note:
            notes = self._append_note(notes, admin_user, note.strip())
        notes = self._append_note(notes, admin_user, "Case escalated for senior review.")

        case = self.case_repository.update(
            case,
            status=FraudCase.Status.ESCALATED,
            investigation_notes=notes,
        )
        self._broadcast_case_escalated(case)
        return case

    def get_timeline(self, fraud_case_id) -> list[dict]:
        case = self.get_case(fraud_case_id)
        alert = case.related_alert
        timeline = []

        timeline.append(
            {
                "timestamp": case.created_at,
                "event_type": "fraud_case_opened",
                "title": "Fraud case opened",
                "description": f"Case created from alert: {alert.title}",
                "source": "fraud_case",
            }
        )
        timeline.append(
            {
                "timestamp": alert.created_at,
                "event_type": "security_alert",
                "title": alert.title,
                "description": alert.description,
                "source": "security_alert",
            }
        )

        since = alert.created_at - timedelta(hours=24)
        audit_qs = self.audit_repository.list_filtered(since=since)
        if case.user_id:
            audit_qs = audit_qs.filter(user_id=case.user_id)
        if case.election_id:
            audit_qs = audit_qs.filter(election_id=case.election_id)

        for log in audit_qs[:50]:
            timeline.append(
                {
                    "timestamp": log.timestamp,
                    "event_type": log.event_type,
                    "title": log.get_event_type_display() if hasattr(log, "get_event_type_display") else log.event_type,
                    "description": f"IP: {log.ip_address or 'unknown'}",
                    "source": "audit_log",
                }
            )

        if case.user_id and case.election_id:
            votes = self.vote_repository.list_for_user_in_election(case.user, case.election)
            for vote in votes:
                timeline.append(
                    {
                        "timestamp": vote.timestamp,
                        "event_type": "vote_cast",
                        "title": f"Vote cast: {vote.position.title}",
                        "description": f"Candidate: {vote.candidate.full_name}",
                        "source": "vote",
                    }
                )

        if alert.device_log_id:
            device = alert.device_log
            timeline.append(
                {
                    "timestamp": device.last_seen_at,
                    "event_type": "device_activity",
                    "title": f"Device: {device.device_type} / {device.operating_system}",
                    "description": device.user_agent[:120],
                    "source": "device_log",
                }
            )

        if alert.location_log_id:
            loc = alert.location_log
            timeline.append(
                {
                    "timestamp": loc.last_seen_at,
                    "event_type": "location_activity",
                    "title": f"Location: {loc.city or loc.country or loc.ip_address}",
                    "description": f"IP {loc.ip_address} — {loc.region}",
                    "source": "location_log",
                }
            )

        timeline.sort(key=lambda item: item["timestamp"])
        return timeline

    def _format_note(self, actor: str, message: str) -> str:
        ts = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"[{ts}] {actor}: {message}"

    def _append_note(self, existing: str, admin_user, message: str) -> str:
        entry = self._format_note(admin_user.get_full_name() or admin_user.email, message)
        if existing:
            return f"{existing}\n{entry}"
        return entry

    def _broadcast_case_resolved(self, case: FraudCase) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.fraud_case_resolved(
                case,
                fraud_stats=dashboard_service.get_fraud_feed_snapshot()["summary"],
            )
        except Exception:
            logger.exception("Failed to broadcast fraud case resolved %s", case.fraud_case_id)

    def _broadcast_case_escalated(self, case: FraudCase) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.fraud_case_escalated(
                case,
                fraud_stats=dashboard_service.get_fraud_feed_snapshot()["summary"],
            )
        except Exception:
            logger.exception("Failed to broadcast fraud case escalated %s", case.fraud_case_id)


fraud_case_service = FraudCaseService()
