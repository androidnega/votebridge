from apps.accounts.models import Role
from apps.elections.models import Election, VoterEligibility
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.fraud.models import FraudCase, SecurityAlert
from apps.fraud.services.alert_service import security_alert_service
from apps.fraud.services.fraud_case_service import fraud_case_service
from apps.security.models import SVTToken
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository


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
        active_elections = Election.objects.filter(status__in=self.ACTIVE_STATUSES).count()
        total_votes = Vote.objects.count()
        eligible_voters = (
            VoterEligibility.objects.filter(is_eligible=True).values("user_id").distinct().count()
        )
        voters_participated = Vote.objects.values("user_id").distinct().count()
        turnout = round((voters_participated / eligible_voters) * 100, 1) if eligible_voters else 0.0

        return {
            "active_elections": active_elections,
            "total_votes_cast": total_votes,
            "registered_voters": eligible_voters,
            "turnout_percentage": turnout,
            "security_alerts": security_alert_service.get_summary(),
            "fraud_cases": fraud_case_service.get_integrity_report(),
        }

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

        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "eligible_voters": eligible_voters,
            "voters_participated": voters_participated,
            "total_votes_cast": total_votes,
            "turnout_percentage": turnout,
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
        }
        return payload

    def get_student_election_status(self, user, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            return {}
        if not self.eligibility_repository.is_user_eligible(election, user):
            return {}
        return self._student_election_row(user, election)

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

    def _student_election_row(self, user, election) -> dict:
        has_submitted = self.vote_repository.list_for_user_in_election(user, election).exists()
        latest_svt = (
            SVTToken.objects.filter(user=user, election=election)
            .order_by("-issued_at")
            .first()
        )
        svt_status = latest_svt.status if latest_svt else None

        if has_submitted:
            confirmation_status = "recorded"
        elif svt_status == SVTToken.Status.VALIDATED:
            confirmation_status = "in_progress"
        elif svt_status == SVTToken.Status.ISSUED:
            confirmation_status = "token_issued"
        else:
            confirmation_status = "not_started"

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "ballot_submitted": has_submitted,
            "svt_status": svt_status,
            "confirmation_status": confirmation_status,
        }

    def _vote_confirmation_summary(self, user, active_elections: list[dict]) -> dict:
        recorded = sum(1 for row in active_elections if row["confirmation_status"] == "recorded")
        in_progress = sum(1 for row in active_elections if row["confirmation_status"] == "in_progress")
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
