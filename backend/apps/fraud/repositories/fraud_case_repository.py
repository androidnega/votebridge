from django.db.models import Count, QuerySet

from apps.fraud.models import FraudCase


class FraudCaseRepository:
    def get_queryset(self) -> QuerySet[FraudCase]:
        return FraudCase.objects.select_related(
            "user",
            "election",
            "related_alert",
            "related_alert__device_log",
            "related_alert__location_log",
        ).all()

    def get_by_fraud_case_id(self, fraud_case_id) -> FraudCase | None:
        return self.get_queryset().filter(fraud_case_id=fraud_case_id).first()

    def get_by_alert_id(self, alert_id) -> FraudCase | None:
        return self.get_queryset().filter(related_alert_id=alert_id).first()

    def create(self, **data) -> FraudCase:
        return FraudCase.objects.create(**data)

    def update(self, case: FraudCase, **fields) -> FraudCase:
        for key, value in fields.items():
            setattr(case, key, value)
        case.save()
        return case

    def list_filtered(
        self,
        status: str | None = None,
        severity: str | None = None,
        election_id: int | None = None,
    ):
        qs = self.get_queryset()
        if status:
            qs = qs.filter(status=status)
        if severity:
            qs = qs.filter(severity=severity)
        if election_id:
            qs = qs.filter(election_id=election_id)
        return qs

    def get_integrity_counts(self) -> dict:
        qs = self.get_queryset()
        total = qs.count()
        open_cases = qs.filter(
            status__in=[FraudCase.Status.OPEN, FraudCase.Status.INVESTIGATING, FraudCase.Status.ESCALATED]
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
        }

    def count_by_severity(self):
        return (
            self.get_queryset()
            .values("severity")
            .annotate(count=Count("fraud_case_id"))
        )

    def count_by_status(self):
        return (
            self.get_queryset()
            .values("status")
            .annotate(count=Count("fraud_case_id"))
        )
