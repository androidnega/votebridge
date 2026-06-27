from django.db.models import Count, QuerySet
from django.utils import timezone

from apps.fraud.models import SecurityAlert


class SecurityAlertRepository:
    def get_queryset(self) -> QuerySet[SecurityAlert]:
        return SecurityAlert.objects.select_related(
            "user",
            "election",
            "device_log",
            "location_log",
            "reviewed_by",
            "resolved_by",
            "escalated_by",
        ).all()

    def get_by_alert_id(self, alert_id) -> SecurityAlert | None:
        return self.get_queryset().filter(alert_id=alert_id).first()

    def create(self, **data) -> SecurityAlert:
        return SecurityAlert.objects.create(**data)

    def update(self, alert: SecurityAlert, **fields) -> SecurityAlert:
        for key, value in fields.items():
            setattr(alert, key, value)
        alert.save()
        return alert

    def list_filtered(
        self,
        status: str | None = None,
        alert_type: str | None = None,
        election_id: int | None = None,
    ):
        qs = self.get_queryset()
        if status:
            qs = qs.filter(status=status)
        if alert_type:
            qs = qs.filter(alert_type=alert_type)
        if election_id:
            qs = qs.filter(election_id=election_id)
        return qs

    def has_open_alert(self, alert_type: str, user_id=None, election_id=None, fingerprint=None) -> bool:
        qs = self.get_queryset().filter(
            alert_type=alert_type,
            status__in=[SecurityAlert.Status.OPEN, SecurityAlert.Status.REVIEWING],
        )
        if user_id:
            qs = qs.filter(user_id=user_id)
        if election_id:
            qs = qs.filter(election_id=election_id)
        if fingerprint:
            qs = qs.filter(metadata__fingerprint=fingerprint)
        return qs.exists()

    def count_by_status(self):
        return (
            self.get_queryset()
            .values("status")
            .annotate(count=Count("alert_id"))
        )
