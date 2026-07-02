from datetime import timedelta

from django.db.models import Count, Min, Q
from django.db.models.functions import TruncHour
from django.utils import timezone

from apps.accounts.models import Role
from apps.candidates.models import Candidate
from apps.elections.models import Election, VoterEligibility, VotingChannel
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.fraud.models import FraudCase, SecurityAlert
from apps.fraud.services.alert_service import security_alert_service
from apps.fraud.services.fraud_case_service import fraud_case_service
from apps.security.models import SVTToken
from apps.ussd.models import USSDSession
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository
from apps.voting.services.vote_service import VoteService


class DashboardService:
    """Aggregated dashboard metrics for REST and WebSocket snapshots."""

    ACTIVE_STATUSES = {Election.Status.OPEN, Election.Status.PAUSED}

    def __init__(
        self,
        election_repository: ElectionRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
        vote_repository: VoteRepository | None = None,
    ):
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.vote_repository = vote_repository or VoteRepository()

    def get_admin_overview(self) -> dict:
        primary_election = (
            Election.objects.filter(status__in=self.ACTIVE_STATUSES).order_by("-start_date").first()
        )
        active_elections = Election.objects.filter(status__in=self.ACTIVE_STATUSES).count()

        if primary_election:
            eligible_voters = VoterEligibility.objects.filter(
                election=primary_election,
                is_eligible=True,
            ).count()
            voters_participated = (
                Vote.objects.filter(election=primary_election).values("user_id").distinct().count()
            )
            total_votes = Vote.objects.filter(election=primary_election).count()
        else:
            eligible_voters = (
                VoterEligibility.objects.filter(is_eligible=True).values("user_id").distinct().count()
            )
            voters_participated = Vote.objects.values("user_id").distinct().count()
            total_votes = Vote.objects.count()

        turnout = round((voters_participated / eligible_voters) * 100, 1) if eligible_voters else 0.0
        trends = self._build_admin_trends(primary_election)
        security_summary = security_alert_service.get_summary()
        fraud_summary = fraud_case_service.get_integrity_report()

        payload = {
            "active_elections": active_elections,
            "total_votes_cast": total_votes,
            "registered_voters": eligible_voters,
            "turnout_percentage": turnout,
            "security_alerts": security_summary,
            "fraud_cases": fraud_summary,
            "trends": trends,
            "monitoring": self._build_admin_monitoring(
                primary_election,
                eligible_voters=eligible_voters,
                voters_participated=voters_participated,
                turnout_percentage=turnout,
                total_votes_cast=total_votes,
                security_summary=security_summary,
                fraud_summary=fraud_summary,
            ),
        }
        if primary_election:
            payload["primary_election"] = {
                "uuid": str(primary_election.uuid),
                "title": primary_election.title,
                "status": primary_election.status,
            }
        return payload

    def _build_admin_trends(self, election: Election | None, hours: int = 24) -> dict:
        election_uuid = str(election.uuid) if election else None
        return {
            "votes_hourly": self._vote_hourly_buckets(election_uuid=election_uuid, hours=hours),
            "turnout_hourly": self._turnout_hourly_buckets(election, hours=hours),
        }

    def _vote_hourly_buckets(self, *, election_uuid: str | None, hours: int = 24) -> list[dict]:
        since = timezone.now() - timedelta(hours=hours)
        queryset = Vote.objects.filter(timestamp__gte=since)
        if election_uuid:
            queryset = queryset.filter(election__uuid=election_uuid)
        else:
            active_ids = Election.objects.filter(status__in=self.ACTIVE_STATUSES).values_list(
                "uuid", flat=True
            )
            queryset = queryset.filter(election__uuid__in=active_ids)

        rows = (
            queryset.annotate(bucket=TruncHour("timestamp"))
            .values("bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        return [{"label": row["bucket"].strftime("%H:00"), "value": row["count"]} for row in rows]

    def _turnout_hourly_buckets(self, election: Election | None, hours: int = 24) -> list[dict]:
        if not election:
            return []

        eligible_voters = VoterEligibility.objects.filter(
            election=election,
            is_eligible=True,
        ).count()
        if not eligible_voters:
            return []

        since = timezone.now() - timedelta(hours=hours)
        first_votes = (
            Vote.objects.filter(election=election, timestamp__gte=since)
            .values("user_id")
            .annotate(first_at=Min("timestamp"))
            .order_by("first_at")
        )
        if not first_votes:
            return []

        cursor = since.replace(minute=0, second=0, microsecond=0)
        end = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        points: list[dict] = []
        vote_times = [row["first_at"] for row in first_votes]
        index = 0
        participated = 0

        while cursor <= end:
            bucket_end = cursor + timedelta(hours=1)
            while index < len(vote_times) and vote_times[index] < bucket_end:
                participated += 1
                index += 1
            turnout = round((participated / eligible_voters) * 100, 1)
            points.append({"label": cursor.strftime("%H:00"), "value": turnout})
            cursor = bucket_end

        return points[-hours:] if len(points) > hours else points

    def _build_admin_monitoring(
        self,
        election: Election | None,
        *,
        eligible_voters: int,
        voters_participated: int,
        turnout_percentage: float,
        total_votes_cast: int,
        security_summary: dict,
        fraud_summary: dict,
    ) -> dict:
        channel_stats = self._channel_vote_stats(election)
        ussd_stats = self._ussd_session_stats(election)
        health = self._system_health_summary()

        return {
            "eligible_voters": eligible_voters,
            "voters_participated": voters_participated,
            "turnout_percentage": turnout_percentage,
            "total_votes_cast": total_votes_cast,
            "web_votes": channel_stats["web_voters"],
            "ussd_votes": channel_stats["ussd_voters"],
            "web_ballots": channel_stats["web_votes"],
            "ussd_ballots": channel_stats["ussd_votes"],
            "active_sessions": ussd_stats["active_sessions"],
            "failed_sessions": ussd_stats["failed_sessions"],
            "security_alerts": security_summary.get("open", 0),
            "fraud_alerts": fraud_summary.get("open_cases", 0),
            "system_health": health,
            "voting_channels": {
                "web_enabled": bool(election.allow_web_voting) if election else False,
                "ussd_enabled": bool(election.allow_ussd_voting) if election else False,
            },
        }

    def _channel_vote_stats(self, election: Election | None) -> dict:
        queryset = Vote.objects.select_related("channel")
        if election:
            queryset = queryset.filter(election=election)
        else:
            active_ids = Election.objects.filter(status__in=self.ACTIVE_STATUSES).values_list(
                "uuid", flat=True
            )
            queryset = queryset.filter(election__uuid__in=active_ids)

        stats = {
            VotingChannel.ChannelName.WEB: {"votes": 0, "voters": 0},
            VotingChannel.ChannelName.USSD: {"votes": 0, "voters": 0},
        }
        rows = queryset.values("channel__channel_name").annotate(
            votes=Count("vote_id"),
            voters=Count("user_id", distinct=True),
        )
        for row in rows:
            channel = row["channel__channel_name"]
            if channel in stats:
                stats[channel] = {"votes": row["votes"], "voters": row["voters"]}

        return {
            "web_votes": stats[VotingChannel.ChannelName.WEB]["votes"],
            "web_voters": stats[VotingChannel.ChannelName.WEB]["voters"],
            "ussd_votes": stats[VotingChannel.ChannelName.USSD]["votes"],
            "ussd_voters": stats[VotingChannel.ChannelName.USSD]["voters"],
        }

    def _ussd_session_stats(self, election: Election | None) -> dict:
        sessions = USSDSession.objects.all()
        if election:
            election_uuid = str(election.uuid)
            sessions = sessions.filter(
                Q(state_data__election_uuid=election_uuid)
                | Q(state_data__vote__election_uuid=election_uuid)
                | Q(completed_vote=True, started_at__gte=election.start_date)
            )
        return {
            "active_sessions": sessions.filter(status=USSDSession.Status.ACTIVE).count(),
            "failed_sessions": sessions.filter(status=USSDSession.Status.FAILED).count(),
        }

    def _system_health_summary(self) -> dict:
        try:
            from apps.operations.services.operations_service import OperationsHealthService

            health = OperationsHealthService().check_all()
            status = health.get("overall_status", "unknown")
            labels = {
                "healthy": "All systems operational",
                "warning": "Some services need attention",
                "critical": "Critical service issues detected",
                "unknown": "Health status unavailable",
            }
            return {
                "status": status,
                "label": labels.get(status, "Health status unavailable"),
                "checked_at": health.get("checked_at"),
            }
        except Exception:
            return {"status": "unknown", "label": "Health status unavailable", "checked_at": None}

    def get_student_overview(self, user) -> dict:
        elections = Election.objects.filter(status__in=self.ACTIVE_STATUSES).order_by("-start_date")
        active = []
        status_counts = {"open": 0, "paused": 0}

        for election in elections:
            if not self.eligibility_repository.is_user_eligible(election, user):
                continue
            if election.status == Election.Status.OPEN:
                status_counts["open"] += 1
            elif election.status == Election.Status.PAUSED:
                status_counts["paused"] += 1

            active.append(self._student_election_row(user, election))

        return {
            "active_elections": active,
            "active_elections_count": len(active),
            "election_status_summary": status_counts,
            "vote_confirmation_status": self._vote_confirmation_summary(user, active),
        }

    def get_election_monitoring(self, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return {}

        eligible_voters = VoterEligibility.objects.filter(
            election=election,
            is_eligible=True,
        ).count()
        voters_participated = (
            Vote.objects.filter(election=election).values("user_id").distinct().count()
        )
        total_votes = Vote.objects.filter(election=election).count()
        turnout = round((voters_participated / eligible_voters) * 100, 1) if eligible_voters else 0.0
        channel_stats = self._channel_vote_stats(election)
        ussd_stats = self._ussd_session_stats(election)

        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "eligible_voters": eligible_voters,
            "voters_participated": voters_participated,
            "total_votes_cast": total_votes,
            "turnout_percentage": turnout,
            "web_votes": channel_stats["web_voters"],
            "ussd_votes": channel_stats["ussd_voters"],
            "web_ballots": channel_stats["web_votes"],
            "ussd_ballots": channel_stats["ussd_votes"],
            "active_sessions": ussd_stats["active_sessions"],
            "failed_sessions": ussd_stats["failed_sessions"],
            "open_alerts": SecurityAlert.objects.filter(
                election=election,
                status__in=[
                    SecurityAlert.Status.OPEN,
                    SecurityAlert.Status.REVIEWING,
                    SecurityAlert.Status.ESCALATED,
                ],
            ).count(),
            "open_fraud_cases": FraudCase.objects.filter(
                election=election,
                status__in=[
                    FraudCase.Status.OPEN,
                    FraudCase.Status.INVESTIGATING,
                    FraudCase.Status.ESCALATED,
                ],
            ).count(),
            "system_health": self._system_health_summary(),
            "voting_channels": {
                "web": election.allow_web_voting,
                "ussd": election.allow_ussd_voting,
            },
        }
        return payload

    def get_student_election_status(self, user, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return {}
        if not self.eligibility_repository.is_user_eligible(election, user):
            return {}
        return self._student_election_row(user, election)

    def get_student_election_detail(self, user, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return {}
        if not self.eligibility_repository.is_user_eligible(election, user):
            return {}

        status_row = self._student_election_row(user, election)
        positions = (
            self.eligibility_repository.get_eligible_positions_for_user(election, user)
            .order_by("display_order", "title")
            .prefetch_related("candidates")
        )

        position_rows = []
        for position in positions:
            candidate_count = position.candidates.filter(status=Candidate.Status.APPROVED).count()
            if candidate_count == 0:
                continue

            votes_cast = self.vote_repository.count_for_user_position(user, position)
            max_votes = position.max_votes_allowed or 1
            position_rows.append(
                {
                    "uuid": str(position.uuid),
                    "title": position.title,
                    "description": position.description,
                    "choice_type": "single" if position.is_single_choice else "multi",
                    "max_votes_allowed": max_votes,
                    "candidate_count": candidate_count,
                    "votes_cast": votes_cast,
                    "has_voted": votes_cast >= max_votes,
                }
            )

        voting_open = election.status == Election.Status.OPEN
        pending_positions = [row for row in position_rows if not row["has_voted"]]

        return {
            **status_row,
            "election_type": election.election_type,
            "election_type_display": election.get_election_type_display(),
            "election_status_display": election.get_status_display(),
            "description": election.description,
            "start_date": election.start_date.isoformat() if election.start_date else None,
            "end_date": election.end_date.isoformat() if election.end_date else None,
            "positions": position_rows,
            "positions_count": len(position_rows),
            "pending_positions_count": len(pending_positions),
            "can_vote": voting_open and bool(pending_positions),
            "next_position_uuid": pending_positions[0]["uuid"] if pending_positions else None,
            "next_position_title": pending_positions[0]["title"] if pending_positions else None,
        }

    def get_security_feed_snapshot(self) -> dict:
        alerts = security_alert_service.list_alerts()[:20]
        return {
            "alerts": [_serialize_alert_feed(alert) for alert in alerts],
            "summary": security_alert_service.get_summary(),
        }

    def get_fraud_feed_snapshot(self) -> dict:
        cases = fraud_case_service.list_cases()[:20]
        return {
            "cases": [_serialize_fraud_feed(case) for case in cases],
            "summary": fraud_case_service.get_integrity_report(),
        }

    def _user_completed_all_positions(self, user, election) -> bool:
        positions = self.eligibility_repository.get_eligible_positions_for_user(election, user)
        position_list = list(positions)
        if not position_list:
            return False
        return all(
            self.vote_repository.count_for_user_position(user, position)
            >= (position.max_votes_allowed or 1)
            for position in position_list
        )

    def _student_election_row(self, user, election) -> dict:
        latest_svt = (
            SVTToken.objects.filter(user=user, election=election)
            .order_by("-issued_at")
            .first()
        )
        svt_status = latest_svt.status if latest_svt else None
        all_positions_voted = self._user_completed_all_positions(user, election)
        has_submitted = bool(latest_svt and latest_svt.status == SVTToken.Status.USED)
        ballot_complete = has_submitted or all_positions_voted

        if ballot_complete:
            confirmation_status = "recorded"
        elif svt_status == SVTToken.Status.VALIDATED:
            confirmation_status = "in_progress"
        elif svt_status == SVTToken.Status.ISSUED:
            confirmation_status = "token_issued"
        else:
            confirmation_status = "not_started"

        confirmation_reference = None
        submitted_at = None
        if has_submitted and latest_svt:
            submitted_at = latest_svt.used_at
            confirmation_reference = VoteService._build_confirmation_reference(latest_svt)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "ballot_submitted": has_submitted,
            "ballot_complete": ballot_complete,
            "svt_status": svt_status,
            "confirmation_status": confirmation_status,
            "confirmation_reference": confirmation_reference,
            "submitted_at": submitted_at,
        }

    def _vote_confirmation_summary(self, user, active_elections: list[dict]) -> dict:
        recorded = sum(
            1 for row in active_elections if row.get("ballot_complete") or row["confirmation_status"] == "recorded"
        )
        in_progress = sum(
            1
            for row in active_elections
            if row["confirmation_status"] in {"in_progress", "partial"}
        )
        pending = sum(
            1
            for row in active_elections
            if row["confirmation_status"] in {"not_started", "token_issued"}
        )
        return {
            "recorded": recorded,
            "in_progress": in_progress,
            "pending": pending,
        }


def _serialize_alert_feed(alert) -> dict:
    return {
        "alert_id": str(alert.alert_id),
        "alert_type": alert.alert_type,
        "status": alert.status,
        "title": alert.title,
        "description": alert.description,
        "user_email": alert.user.email if alert.user else None,
        "election_title": alert.election.title if alert.election else None,
        "created_at": alert.created_at.isoformat(),
    }


def _serialize_fraud_feed(case) -> dict:
    alert = case.related_alert
    return {
        "fraud_case_id": str(case.fraud_case_id),
        "alert_title": alert.title,
        "severity": case.severity,
        "status": case.status,
        "risk_score": case.risk_score,
        "election_title": case.election.title if case.election else None,
        "created_at": case.created_at.isoformat(),
    }


dashboard_service = DashboardService()
