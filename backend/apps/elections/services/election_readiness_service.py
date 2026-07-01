"""Enterprise election readiness validation (RC2)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.elections.models import Election
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.elections.services.voting_channel_service import VotingChannelService
from apps.elections.validators import validate_election_can_be_opened, validate_election_dates
from apps.fraud.services.fraud_case_service import FraudCaseService
from apps.operations.services.operations_service import OperationsHealthService
from apps.system.repositories.system_repository import SystemSettingRepository
from apps.system.services.feature_flag_service import feature_flag_service
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")


@dataclass
class ReadinessCheckResult:
    key: str
    label: str
    passed: bool
    critical: bool
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ElectionReadinessReport:
    election_uuid: str
    election_title: str
    election_status: str
    is_ready: bool
    readiness_score: int
    checks: dict
    blocking_issues: list[str]
    warnings: list[str]
    validated_at: str

    def to_dict(self) -> dict:
        return {
            "election_uuid": self.election_uuid,
            "election_title": self.election_title,
            "election_status": self.election_status,
            "is_ready": self.is_ready,
            "readiness_score": self.readiness_score,
            "checks": self.checks,
            "blocking_issues": self.blocking_issues,
            "warnings": self.warnings,
            "validated_at": self.validated_at,
        }


class ElectionReadinessService:
    """Pre-open validation — composes existing platform services only."""

    def __init__(
        self,
        eligibility_repository: VoterEligibilityRepository | None = None,
        channel_service: VotingChannelService | None = None,
        health_service: OperationsHealthService | None = None,
        fraud_service: FraudCaseService | None = None,
        settings_repository: SystemSettingRepository | None = None,
    ):
        self.eligibility = eligibility_repository or VoterEligibilityRepository()
        self.channels = channel_service or VotingChannelService()
        self.health = health_service or OperationsHealthService()
        self.fraud = fraud_service or FraudCaseService()
        self.settings = settings_repository or SystemSettingRepository()

    def assess(self, election: Election, *, actor=None) -> ElectionReadinessReport:
        checks: list[ReadinessCheckResult] = []
        checks.append(self._check_election_dates(election))
        checks.append(self._check_ballot_structure(election))
        checks.append(self._check_eligible_voters(election))
        checks.extend(self._check_voting_policies(election))
        checks.append(self._check_strongroom(election))
        checks.append(self._check_fraud_monitoring(election))
        checks.append(self._check_audit_logging())
        checks.extend(self._check_infrastructure(election))
        checks.extend(self._check_integrations(election))

        blocking = [c.message for c in checks if c.critical and not c.passed]
        warnings = [c.message for c in checks if not c.critical and not c.passed]
        passed = sum(1 for c in checks if c.passed)
        score = int(round((passed / len(checks)) * 100)) if checks else 0
        if blocking:
            score = min(score, 79)

        report = ElectionReadinessReport(
            election_uuid=str(election.uuid),
            election_title=election.title,
            election_status=election.status,
            is_ready=len(blocking) == 0,
            readiness_score=score,
            checks={
                c.key: {
                    "label": c.label,
                    "passed": c.passed,
                    "critical": c.critical,
                    "message": c.message,
                    "details": c.details,
                }
                for c in checks
            },
            blocking_issues=blocking,
            warnings=warnings,
            validated_at=timezone.now().isoformat(),
        )
        self._log_validation(election, report, actor)
        return report

    def validate_for_open(self, election: Election, *, actor=None) -> ElectionReadinessReport:
        report = self.assess(election, actor=actor)
        if not report.is_ready:
            raise ValidationError(
                message="; ".join(report.blocking_issues[:8]),
                code="election_not_ready",
            )
        return report

    def _check_election_dates(self, election: Election) -> ReadinessCheckResult:
        if not election.start_date or not election.end_date:
            return self._result(
                "election_dates",
                "Election dates configured",
                False,
                True,
                "Start and end dates must be configured before opening.",
            )
        try:
            validate_election_dates(election.start_date, election.end_date)
            now = timezone.now()
            if election.end_date <= now:
                return self._result(
                    "election_dates",
                    "Election dates configured",
                    False,
                    True,
                    "Election end date must be in the future.",
                    {"end_date": election.end_date.isoformat()},
                )
            return self._result(
                "election_dates",
                "Election dates configured",
                True,
                True,
                "Election window is valid.",
                {
                    "start_date": election.start_date.isoformat(),
                    "end_date": election.end_date.isoformat(),
                },
            )
        except DjangoValidationError as exc:
            return self._result(
                "election_dates",
                "Election dates configured",
                False,
                True,
                str(exc.message),
            )

    def _check_ballot_structure(self, election: Election) -> ReadinessCheckResult:
        try:
            validate_election_can_be_opened(election)
            position_count = election.positions.filter(is_active=True).count()
            candidate_count = election.candidates.filter(status="approved").count()
            return self._result(
                "ballot_structure",
                "Positions and candidates",
                True,
                True,
                "All active positions have approved candidates.",
                {"positions": position_count, "approved_candidates": candidate_count},
            )
        except DjangoValidationError as exc:
            return self._result(
                "ballot_structure",
                "Positions and candidates",
                False,
                True,
                str(exc.message),
            )

    def _check_eligible_voters(self, election: Election) -> ReadinessCheckResult:
        count = self.eligibility.get_eligible_voters_for_election(election).count()
        if count < 1:
            return self._result(
                "eligible_voters",
                "Eligible voters imported",
                False,
                True,
                "At least one eligible voter must be registered for this election.",
                {"eligible_count": 0},
            )
        return self._result(
            "eligible_voters",
            "Eligible voters imported",
            True,
            True,
            f"{count} eligible voter(s) registered.",
            {"eligible_count": count},
        )

    def _check_voting_policies(self, election: Election) -> list[ReadinessCheckResult]:
        results: list[ReadinessCheckResult] = []
        enabled_channels = []
        if election.allow_web_voting:
            enabled_channels.append("web")
        if election.allow_ussd_voting:
            enabled_channels.append("ussd")
        if election.allow_sms_notifications:
            enabled_channels.append("sms")

        if not enabled_channels:
            results.append(
                self._result(
                    "voting_policies",
                    "Voting policies configured",
                    False,
                    True,
                    "Enable at least one voting channel (web, USSD, or SMS notifications).",
                )
            )
            return results

        active_registry = {
            c.channel_name
            for c in self.channels.list_channels(active_only=True)
        }
        missing = [name for name in enabled_channels if name not in active_registry]
        svt_required = self._setting_bool("election_policies", "require_svt", True)

        results.append(
            self._result(
                "voting_policies",
                "Voting policies configured",
                not missing,
                True,
                "All enabled channels are active in the voting registry."
                if not missing
                else f"Missing active registry entries: {', '.join(missing)}.",
                {
                    "enabled_channels": enabled_channels,
                    "active_registry": sorted(active_registry),
                    "require_svt": svt_required,
                },
            )
        )
        return results

    def _check_strongroom(self, election: Election) -> ReadinessCheckResult:
        try:
            from apps.strongroom.services.integrity_verification_service import (
                integrity_verification_service,
            )

            dashboard = integrity_verification_service.get_dashboard(election.uuid)
            seal_status = dashboard.get("seal_status", "pending")
            if seal_status == "locked" and election.status not in (
                Election.Status.CLOSED,
                Election.Status.ARCHIVED,
            ):
                return self._result(
                    "strongroom",
                    "Strongroom initialized",
                    False,
                    True,
                    "Election strongroom is locked before voting has completed.",
                    {"seal_status": seal_status},
                )
            return self._result(
                "strongroom",
                "Strongroom initialized",
                True,
                True,
                "Strongroom subsystem is available for this election.",
                {"seal_status": seal_status},
            )
        except Exception as exc:
            logger.warning("Strongroom readiness check failed: %s", exc)
            return self._result(
                "strongroom",
                "Strongroom initialized",
                False,
                True,
                f"Strongroom subsystem unavailable: {exc}",
            )

    def _check_fraud_monitoring(self, election: Election) -> ReadinessCheckResult:
        enabled = feature_flag_service.is_enabled("fraud_detection")
        if not enabled:
            return self._result(
                "fraud_monitoring",
                "Fraud monitoring enabled",
                False,
                True,
                "Fraud detection feature flag must be enabled before opening.",
            )
        report = self.fraud.get_integrity_report(election_uuid=str(election.uuid))
        critical = report.get("critical_cases", 0)
        if critical > 0:
            return self._result(
                "fraud_monitoring",
                "Fraud monitoring enabled",
                False,
                True,
                f"{critical} critical fraud case(s) must be resolved before opening.",
                report,
            )
        return self._result(
            "fraud_monitoring",
            "Fraud monitoring enabled",
            True,
            True,
            "Fraud monitoring is active with no critical open cases.",
            report,
        )

    def _check_audit_logging(self) -> ReadinessCheckResult:
        level = self._setting_value("audit", "audit_level", "standard")
        retention = int(self._setting_value("audit", "retention_days", 365))
        passed = level not in ("none", "off", "") and retention > 0
        return self._result(
            "audit_logging",
            "Audit logging enabled",
            passed,
            True,
            "Audit logging is configured."
            if passed
            else "Audit logging must be enabled with retention configured.",
            {"audit_level": level, "retention_days": retention},
        )

    def _check_infrastructure(self, election: Election) -> list[ReadinessCheckResult]:
        health = self.health.check_all()
        by_name = {c["name"]: c for c in health.get("components", [])}
        results = []

        for key, label, component_name in (
            ("postgresql", "PostgreSQL healthy", "database"),
            ("redis", "Redis healthy", "redis"),
            ("websockets", "WebSocket infrastructure healthy", "websockets"),
        ):
            component = by_name.get(component_name, {})
            status = component.get("status", "unknown")
            passed = status in ("healthy", "warning")
            critical = status == "critical" or (status == "unknown" and key != "websockets")
            if key == "websockets" and status == "unknown":
                passed = True
                critical = False
            results.append(
                self._result(
                    key,
                    label,
                    passed and status != "critical",
                    critical or status == "critical",
                    component.get("details", f"{label} check: {status}"),
                    {"status": status, **{k: v for k, v in component.items() if k not in ("name",)}},
                )
            )
        return results

    def _check_integrations(self, election: Election) -> list[ReadinessCheckResult]:
        health = self.health.check_all()
        by_name = {c["name"]: c for c in health.get("components", [])}
        results: list[ReadinessCheckResult] = []

        if election.allow_ussd_voting:
            ussd = by_name.get("ussd", {})
            status = ussd.get("status", "unknown")
            results.append(
                self._result(
                    "ussd_integration",
                    "USSD integration available",
                    status != "critical",
                    True,
                    ussd.get("details", f"USSD status: {status}"),
                    {"status": status},
                )
            )

        if election.allow_sms_notifications:
            comms = by_name.get("communications", {})
            status = comms.get("status", "unknown")
            results.append(
                self._result(
                    "sms_integration",
                    "SMS integration available",
                    status in ("healthy", "warning"),
                    True,
                    comms.get("details", f"SMS provider status: {status}"),
                    {"status": status},
                )
            )

        return results

    def _setting_value(self, category: str, key: str, default):
        setting = self.settings.get_by_key(f"{category}.{key}")
        if not setting:
            return default
        return setting.value.get("value", default)

    def _setting_bool(self, category: str, key: str, default: bool) -> bool:
        return bool(self._setting_value(category, key, default))

    @staticmethod
    def _result(
        key: str,
        label: str,
        passed: bool,
        critical: bool,
        message: str,
        details: dict | None = None,
    ) -> ReadinessCheckResult:
        return ReadinessCheckResult(
            key=key,
            label=label,
            passed=passed,
            critical=critical,
            message=message,
            details=details or {},
        )

    @staticmethod
    def _log_validation(election: Election, report: ElectionReadinessReport, actor) -> None:
        try:
            from apps.security.models import AuditLog
            from apps.security.services.monitoring_service import monitoring_service

            monitoring_service.record_event(
                event_type=AuditLog.EventType.ADMIN_ACTION,
                user=actor,
                metadata={
                    "action": "election_readiness_validated",
                    "election_uuid": str(election.uuid),
                    "election_title": election.title,
                    "is_ready": report.is_ready,
                    "readiness_score": report.readiness_score,
                    "blocking_issues": report.blocking_issues,
                    "warnings": report.warnings,
                    "validated_at": report.validated_at,
                },
                election_uuid=str(election.uuid),
            )
        except Exception:
            logger.exception("Failed to log election readiness validation for %s", election.uuid)


election_readiness_service = ElectionReadinessService()
