from datetime import timedelta

from django.db.models import Avg, Count, F, Q, QuerySet
from django.utils import timezone

from apps.ussd.models import USSDRequestLog, USSDSession


class USSDSessionRepository:
    def get_queryset(self) -> QuerySet[USSDSession]:
        return USSDSession.objects.select_related("user")

    def get_by_session_id(self, session_id: str) -> USSDSession | None:
        return self.get_queryset().filter(session_id=session_id).first()

    def create(self, **kwargs) -> USSDSession:
        return USSDSession.objects.create(**kwargs)

    def save(self, session: USSDSession) -> USSDSession:
        session.save()
        return session

    def list_filtered(
        self,
        *,
        status: str | None = None,
        msisdn: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[USSDSession], int]:
        qs = self.get_queryset()
        if status:
            qs = qs.filter(status=status)
        if msisdn:
            qs = qs.filter(msisdn__icontains=msisdn)
        if search:
            qs = qs.filter(
                Q(session_id__icontains=search)
                | Q(msisdn__icontains=search)
                | Q(user__index_number__icontains=search)
            )
        total = qs.count()
        return list(qs[offset : offset + limit]), total

    def expire_stale(self, timeout_minutes: int) -> int:
        cutoff = timezone.now() - timedelta(minutes=timeout_minutes)
        stale = self.get_queryset().filter(
            status=USSDSession.Status.ACTIVE,
            last_activity_at__lt=cutoff,
        )
        count = 0
        for session in stale:
            if session.state_data.get("vote") and not session.completed_vote:
                session.status = USSDSession.Status.ABANDONED
            else:
                session.status = USSDSession.Status.EXPIRED
            session.ended_at = timezone.now()
            session.save(update_fields=["status", "ended_at"])
            count += 1
        return count

    def reset_session(
        self,
        session: USSDSession,
        *,
        msisdn: str,
        service_code: str = "",
        network: str = "",
    ) -> tuple[USSDSession, str]:
        """Reuse carrier session_id after expiry/completion — Arkesel lifecycle recovery."""
        previous_status = session.status
        session.status = USSDSession.Status.ACTIVE
        session.current_step = "WELCOME"
        session.state_data = {"pending_auth_target": None, "_recovered_from": previous_status}
        session.user = None
        session.completed_vote = False
        session.failure_reason = ""
        session.request_count = 0
        session.started_at = timezone.now()
        session.last_activity_at = timezone.now()
        session.ended_at = None
        if msisdn:
            session.msisdn = msisdn
        if service_code:
            session.service_code = service_code
        if network:
            session.network = network
        session.save()
        return session, previous_status

    def dashboard_stats(self) -> dict:
        today = timezone.now().date()
        sessions = USSDSession.objects.all()
        logs = USSDRequestLog.objects.all()
        completed = sessions.filter(status=USSDSession.Status.COMPLETED)
        avg_duration = (
            completed.filter(ended_at__isnull=False)
            .annotate(duration=F("ended_at") - F("started_at"))
            .aggregate(avg=Avg("duration"))
        )
        return {
            "active_sessions": sessions.filter(status=USSDSession.Status.ACTIVE).count(),
            "completed_votes": sessions.filter(completed_vote=True).count(),
            "abandoned_sessions": sessions.filter(status=USSDSession.Status.ABANDONED).count(),
            "failed_sessions": sessions.filter(status=USSDSession.Status.FAILED).count(),
            "expired_sessions": sessions.filter(status=USSDSession.Status.EXPIRED).count(),
            "successful_requests": logs.filter(outcome=USSDRequestLog.Outcome.SUCCESS).count(),
            "failed_requests": logs.filter(outcome=USSDRequestLog.Outcome.ERROR).count(),
            "requests_today": logs.filter(created_at__date=today).count(),
            "sessions_today": sessions.filter(started_at__date=today).count(),
            "average_session_seconds": (
                avg_duration["avg"].total_seconds() if avg_duration["avg"] else 0
            ),
            "provider_status": "configured",
        }


class USSDRequestLogRepository:
    def get_queryset(self) -> QuerySet[USSDRequestLog]:
        return USSDRequestLog.objects.select_related("session", "session__user")

    def create(self, **kwargs) -> USSDRequestLog:
        return USSDRequestLog.objects.create(**kwargs)

    def list_filtered(
        self,
        *,
        outcome: str | None = None,
        msisdn: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[USSDRequestLog], int]:
        qs = self.get_queryset()
        if outcome:
            qs = qs.filter(outcome=outcome)
        if msisdn:
            qs = qs.filter(msisdn__icontains=msisdn)
        if search:
            qs = qs.filter(
                Q(carrier_session_id__icontains=search)
                | Q(msisdn__icontains=search)
                | Q(raw_input__icontains=search)
            )
        total = qs.count()
        return list(qs[offset : offset + limit]), total
