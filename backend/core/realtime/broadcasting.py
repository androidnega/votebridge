import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone

from core.realtime import events, groups
from core.realtime.sanitize import sanitize_payload

logger = logging.getLogger("votebridge")


class RealtimeBroadcastService:
    """Publishes sanitized real-time events to Redis channel groups."""

    def broadcast(self, event_type: str, payload: dict, group_names: list[str]) -> None:
        if not group_names:
            return

        election_status = payload.get("election_status")
        safe_payload = sanitize_payload(payload, election_status=election_status)
        timestamp = timezone.now().isoformat()

        def _send() -> None:
            channel_layer = get_channel_layer()
            if channel_layer is None:
                logger.debug("Channel layer unavailable; skipping broadcast for %s", event_type)
                return

            message = {
                "type": "realtime.event",
                "event_type": event_type,
                "payload": safe_payload,
                "timestamp": timestamp,
            }
            for group_name in group_names:
                try:
                    async_to_sync(channel_layer.group_send)(group_name, message)
                except Exception:
                    logger.exception("Failed to broadcast %s to %s", event_type, group_name)

        transaction.on_commit(_send)

    def election_opened(self, election) -> None:
        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "start_date": election.start_date.isoformat(),
            "end_date": election.end_date.isoformat(),
        }
        self.broadcast(
            events.ELECTION_OPENED,
            payload,
            [groups.election(election.uuid), groups.dashboard_admin()],
        )

    def election_closed(self, election) -> None:
        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "end_date": election.end_date.isoformat(),
        }
        self.broadcast(
            events.ELECTION_CLOSED,
            payload,
            [groups.election(election.uuid), groups.dashboard_admin()],
        )

    def ballot_submitted(
        self,
        *,
        election,
        user,
        positions_completed: list[str],
        positions_count: int,
        votes_count: int,
        admin_stats: dict | None = None,
        student_stats: dict | None = None,
    ) -> None:
        base = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "positions_count": positions_count,
            "votes_count": votes_count,
        }
        voter_payload = {
            **base,
            "user_uuid": str(user.uuid),
            "positions_completed": positions_completed,
            "ballot_submitted": True,
            "confirmation_status": "recorded",
        }
        admin_payload = {**base, **(admin_stats or {})}

        self.broadcast(
            events.BALLOT_SUBMITTED,
            voter_payload,
            [
                groups.election(election.uuid),
                groups.dashboard_student(user.uuid),
            ],
        )
        self.broadcast(
            events.BALLOT_SUBMITTED,
            admin_payload,
            [groups.dashboard_admin(), groups.election(election.uuid)],
        )
        if student_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "student", **student_stats},
                [groups.dashboard_student(user.uuid)],
            )
        if admin_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **admin_stats},
                [groups.dashboard_admin()],
            )

    def svt_issued(self, *, svt, user, admin_stats: dict | None = None) -> None:
        payload = {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(svt.election.uuid),
            "election_title": svt.election.title,
            "election_status": svt.election.status,
            "user_uuid": str(user.uuid),
            "status": svt.status,
            "expires_at": svt.expires_at.isoformat(),
        }
        self.broadcast(
            events.SVT_ISSUED,
            payload,
            [
                groups.dashboard_student(user.uuid),
                groups.election(svt.election.uuid),
                groups.dashboard_admin(),
            ],
        )
        if admin_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **admin_stats},
                [groups.dashboard_admin()],
            )

    def svt_validated(self, *, svt, user, student_stats: dict | None = None) -> None:
        payload = {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(svt.election.uuid),
            "election_title": svt.election.title,
            "election_status": svt.election.status,
            "user_uuid": str(user.uuid),
            "status": svt.status,
        }
        self.broadcast(
            events.SVT_VALIDATED,
            payload,
            [
                groups.dashboard_student(user.uuid),
                groups.election(svt.election.uuid),
            ],
        )
        if student_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "student", **student_stats},
                [groups.dashboard_student(user.uuid)],
            )

    def svt_consumed(
        self,
        *,
        svt,
        user,
        vote_count: int,
        admin_stats: dict | None = None,
        student_stats: dict | None = None,
    ) -> None:
        payload = {
            "svt_id": str(svt.svt_id),
            "election_uuid": str(svt.election.uuid),
            "election_title": svt.election.title,
            "election_status": svt.election.status,
            "user_uuid": str(user.uuid),
            "status": svt.status,
            "vote_count": vote_count,
        }
        self.broadcast(
            events.SVT_CONSUMED,
            payload,
            [
                groups.dashboard_student(user.uuid),
                groups.election(svt.election.uuid),
            ],
        )
        if admin_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **admin_stats},
                [groups.dashboard_admin()],
            )
        if student_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "student", **student_stats},
                [groups.dashboard_student(user.uuid)],
            )

    def security_alert_created(self, alert, admin_stats: dict | None = None) -> None:
        payload = _serialize_alert(alert)
        target_groups = [groups.security(), groups.dashboard_admin()]
        if alert.election_id:
            target_groups.append(groups.election(alert.election.uuid))
        self.broadcast(events.SECURITY_ALERT_CREATED, payload, target_groups)
        if admin_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **admin_stats},
                [groups.dashboard_admin()],
            )

    def security_alert_resolved(self, alert, admin_stats: dict | None = None) -> None:
        payload = _serialize_alert(alert)
        target_groups = [groups.security(), groups.dashboard_admin()]
        if alert.election_id:
            target_groups.append(groups.election(alert.election.uuid))
        self.broadcast(events.SECURITY_ALERT_RESOLVED, payload, target_groups)
        if admin_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **admin_stats},
                [groups.dashboard_admin()],
            )

    def fraud_case_created(self, case, fraud_stats: dict | None = None) -> None:
        payload = _serialize_fraud_case(case)
        target_groups = [groups.fraud(), groups.dashboard_admin()]
        if case.election_id:
            target_groups.append(groups.election(case.election.uuid))
        self.broadcast(events.FRAUD_CASE_CREATED, payload, target_groups)
        if fraud_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", "fraud_cases": fraud_stats},
                [groups.dashboard_admin(), groups.fraud()],
            )

    def fraud_case_resolved(self, case, fraud_stats: dict | None = None) -> None:
        payload = _serialize_fraud_case(case)
        target_groups = [groups.fraud(), groups.dashboard_admin()]
        if case.election_id:
            target_groups.append(groups.election(case.election.uuid))
        self.broadcast(events.FRAUD_CASE_RESOLVED, payload, target_groups)
        if fraud_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", "fraud_cases": fraud_stats},
                [groups.dashboard_admin(), groups.fraud()],
            )

    def fraud_case_escalated(self, case, fraud_stats: dict | None = None) -> None:
        payload = _serialize_fraud_case(case)
        target_groups = [groups.fraud(), groups.dashboard_admin()]
        if case.election_id:
            target_groups.append(groups.election(case.election.uuid))
        self.broadcast(events.FRAUD_CASE_ESCALATED, payload, target_groups)
        if fraud_stats:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", "fraud_cases": fraud_stats},
                [groups.dashboard_admin(), groups.fraud()],
            )

    def dashboard_stats(self, *, role: str, user_uuid, payload: dict) -> None:
        if role == "admin":
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "admin", **payload},
                [groups.dashboard_admin()],
            )
        elif role == "student" and user_uuid:
            self.broadcast(
                events.DASHBOARD_STATS,
                {"role": "student", **payload},
                [groups.dashboard_student(user_uuid)],
            )

    def results_generated(self, result) -> None:
        payload = _serialize_election_result(result, include_standings=True)
        self.broadcast(
            events.RESULTS_GENERATED,
            payload,
            [groups.results(), groups.dashboard_admin(), groups.election(result.election.uuid)],
        )

    def results_certified(self, result) -> None:
        payload = _serialize_election_result(result, include_standings=True)
        self.broadcast(
            events.RESULTS_CERTIFIED,
            payload,
            [groups.results(), groups.dashboard_admin(), groups.election(result.election.uuid)],
        )

    def results_published(self, result) -> None:
        payload = _serialize_election_result(result, include_standings=True)
        target = [groups.results(), groups.dashboard_admin(), groups.election(result.election.uuid)]
        self.broadcast(events.RESULTS_PUBLISHED, payload, target)

    def strongroom_sealed(self, ballot_seal) -> None:
        payload = {
            "ballot_seal_uuid": str(ballot_seal.uuid),
            "election_uuid": str(ballot_seal.election.uuid),
            "election_title": ballot_seal.election.title,
            "election_status": ballot_seal.election.status,
            "seal_hash": ballot_seal.seal_hash,
            "vote_count": ballot_seal.vote_count,
            "status": ballot_seal.status,
        }
        self.broadcast(
            events.STRONGROOM_SEALED,
            payload,
            [groups.strongroom(), groups.dashboard_admin(), groups.election(ballot_seal.election.uuid)],
        )

    def strongroom_verified(self, election, verification) -> None:
        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "verification_uuid": str(verification.uuid),
            "integrity_score": verification.integrity_score,
            "is_valid": verification.is_valid,
            "verification_type": verification.verification_type,
        }
        self.broadcast(
            events.STRONGROOM_VERIFIED,
            payload,
            [groups.strongroom(), groups.dashboard_admin()],
        )

    def election_locked(self, election_seal) -> None:
        payload = {
            "election_uuid": str(election_seal.election.uuid),
            "election_title": election_seal.election.title,
            "election_status": election_seal.election.status,
            "seal_status": election_seal.status,
            "election_seal_hash": election_seal.election_seal_hash,
            "locked_at": election_seal.locked_at.isoformat() if election_seal.locked_at else None,
        }
        self.broadcast(
            events.ELECTION_LOCKED,
            payload,
            [groups.strongroom(), groups.dashboard_admin(), groups.election(election_seal.election.uuid)],
        )

    def integrity_check_completed(self, election, verification) -> None:
        payload = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "verification_uuid": str(verification.uuid),
            "integrity_score": verification.integrity_score,
            "is_valid": verification.is_valid,
        }
        self.broadcast(
            events.INTEGRITY_CHECK_COMPLETED,
            payload,
            [groups.strongroom(), groups.dashboard_admin()],
        )

    def communication_delivery_updated(self, delivery_log) -> None:
        payload = {
            "delivery_uuid": str(delivery_log.uuid),
            "channel": delivery_log.channel,
            "status": delivery_log.status,
            "template_code": delivery_log.template_code,
            "recipient": delivery_log.recipient[:4] + "***" if delivery_log.recipient else "",
        }
        self.broadcast(
            events.COMMUNICATION_DELIVERY_UPDATED,
            payload,
            [groups.communications(), groups.dashboard_admin()],
        )

    def in_app_notification_created(self, notification) -> None:
        payload = {
            "notification_uuid": str(notification.uuid),
            "title": notification.title,
            "category": notification.category,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        }
        group_names = [groups.communications(), groups.dashboard_admin()]
        if notification.user_id:
            group_names.append(groups.user_notifications(notification.user.uuid))
        self.broadcast(events.IN_APP_NOTIFICATION_CREATED, payload, group_names)

    def ussd_session_updated(self, session, continue_session: bool) -> None:
        payload = {
            "session_uuid": str(session.uuid),
            "session_id": session.session_id,
            "msisdn": session.msisdn[-4:].rjust(len(session.msisdn), "*") if session.msisdn else "",
            "status": session.status,
            "current_step": session.current_step,
            "completed_vote": session.completed_vote,
            "continue_session": continue_session,
        }
        groups_list = [groups.ussd(), groups.dashboard_admin()]
        self.broadcast(events.USSD_SESSION_UPDATED, payload, groups_list)
        if session.completed_vote:
            self.broadcast(events.USSD_VOTE_COMPLETED, payload, groups_list)


def _serialize_alert(alert) -> dict:
    return {
        "alert_id": str(alert.alert_id),
        "alert_type": alert.alert_type,
        "status": alert.status,
        "title": alert.title,
        "description": alert.description,
        "user_email": alert.user.email if alert.user else None,
        "user_name": alert.user.get_full_name() if alert.user else None,
        "election_uuid": str(alert.election.uuid) if alert.election else None,
        "election_title": alert.election.title if alert.election else None,
        "election_status": alert.election.status if alert.election else None,
        "created_at": alert.created_at.isoformat(),
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "metadata": alert.metadata or {},
    }


def _serialize_fraud_case(case) -> dict:
    alert = case.related_alert
    return {
        "fraud_case_id": str(case.fraud_case_id),
        "election_uuid": str(case.election.uuid) if case.election else None,
        "election_title": case.election.title if case.election else None,
        "election_status": case.election.status if case.election else None,
        "user_uuid": str(case.user.uuid) if case.user else None,
        "user_email": case.user.email if case.user else None,
        "user_name": case.user.get_full_name() if case.user else None,
        "related_alert_id": str(alert.alert_id),
        "alert_type": alert.alert_type,
        "alert_title": alert.title,
        "risk_score": case.risk_score,
        "severity": case.severity,
        "status": case.status,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
    }


def _serialize_election_result(result, *, include_standings: bool = False) -> dict:
    from apps.elections.models import Election

    payload = {
        "result_uuid": str(result.uuid),
        "election_uuid": str(result.election.uuid),
        "election_title": result.election.title,
        "election_status": result.election.status,
        "result_status": result.status,
        "turnout_percentage": float(result.turnout_percentage),
        "total_votes_cast": result.total_votes_cast,
        "eligible_voters": result.eligible_voters,
        "generated_at": result.generated_at.isoformat() if result.generated_at else None,
        "certified_at": result.certified_at.isoformat() if result.certified_at else None,
        "published_at": result.published_at.isoformat() if result.published_at else None,
    }
    if include_standings and result.election.status != Election.Status.OPEN:
        payload["standings"] = result.standings
    return payload


realtime_broadcast_service = RealtimeBroadcastService()
