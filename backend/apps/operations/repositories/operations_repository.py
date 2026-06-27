from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.accounts.models import Role, Session
from apps.elections.models import Election
from apps.fraud.models import FraudCase, SecurityAlert
from apps.results.models import ElectionResult
from apps.strongroom.models import ElectionSeal
from apps.voting.models import Vote


class OperationsRepository:
    """Read-only aggregation queries for the Enterprise Operations Center."""

    ACTIVE_ELECTION_STATUSES = {Election.Status.OPEN, Election.Status.PAUSED}

    def election_counts(self) -> dict:
        rows = Election.objects.values("status").annotate(count=Count("id"))
        counts = {row["status"]: row["count"] for row in rows}
        return {
            "open": counts.get(Election.Status.OPEN, 0),
            "scheduled": counts.get(Election.Status.SCHEDULED, 0),
            "paused": counts.get(Election.Status.PAUSED, 0),
            "closed": counts.get(Election.Status.CLOSED, 0),
            "archived": counts.get(Election.Status.ARCHIVED, 0),
            "draft": counts.get(Election.Status.DRAFT, 0),
        }

    def active_elections(self):
        return (
            Election.objects.filter(status__in=self.ACTIVE_ELECTION_STATUSES)
            .order_by("-start_date")
            .select_related("created_by")
        )

    def session_stats(self) -> dict:
        now = timezone.now()
        active_qs = Session.objects.filter(is_active=True, expires_at__gt=now)
        expired_qs = Session.objects.filter(expires_at__lte=now, is_active=True)
        revoked_qs = Session.objects.filter(is_active=False)

        role_counts = (
            active_qs.values("user__role__name")
            .annotate(count=Count("uuid"))
            .order_by()
        )
        by_role = {row["user__role__name"]: row["count"] for row in role_counts}

        duplicate_devices = (
            active_qs.values("user_id", "ip_address")
            .annotate(session_count=Count("uuid"))
            .filter(session_count__gt=1)
            .count()
        )

        return {
            "authenticated_sessions": active_qs.count(),
            "expired_sessions": expired_qs.count(),
            "blocked_sessions": revoked_qs.count(),
            "students_online": by_role.get(Role.Name.STUDENT, 0),
            "candidates_online": by_role.get(Role.Name.CANDIDATE, 0),
            "admins_online": by_role.get(Role.Name.ADMIN, 0),
            "super_admins_online": by_role.get(Role.Name.SUPER_ADMIN, 0),
            "multiple_device_sessions": duplicate_devices,
        }

    def pending_workloads(self) -> dict:
        return {
            "pending_certification": ElectionResult.objects.filter(
                status=ElectionResult.Status.PENDING_CERTIFICATION
            ).count(),
            "pending_publication": ElectionResult.objects.filter(
                status=ElectionResult.Status.CERTIFIED
            ).count(),
            "pending_strongroom_verification": ElectionSeal.objects.filter(
                status=ElectionSeal.Status.PENDING
            ).count(),
            "pending_fraud_investigations": FraudCase.objects.filter(
                status__in=[
                    FraudCase.Status.OPEN,
                    FraudCase.Status.INVESTIGATING,
                    FraudCase.Status.ESCALATED,
                ]
            ).count(),
            "pending_security_alerts": SecurityAlert.objects.filter(
                status__in=[
                    SecurityAlert.Status.OPEN,
                    SecurityAlert.Status.REVIEWING,
                    SecurityAlert.Status.ESCALATED,
                ]
            ).count(),
        }

    def recent_votes_count(self, hours: int = 1) -> int:
        since = timezone.now() - timedelta(hours=hours)
        return Vote.objects.filter(timestamp__gte=since).count()

    def online_users_estimate(self) -> int:
        since = timezone.now() - timedelta(minutes=15)
        return (
            Session.objects.filter(is_active=True, last_activity_at__gte=since)
            .values("user_id")
            .distinct()
            .count()
        )
