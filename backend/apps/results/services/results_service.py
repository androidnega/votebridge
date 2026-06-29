import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from apps.elections.models import Election, Position, VoterEligibility
from apps.elections.repositories.election_repository import ElectionRepository
from apps.fraud.models import FraudCase, SecurityAlert
from apps.results.models import ElectionResult
from apps.results.repositories.election_result_repository import ElectionResultRepository
from apps.results.validators import validate_election_closed_for_results
from apps.security.models import AuditLog, SVTToken
from apps.voting.repositories.vote_repository import VoteRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class ResultIntegrityService:
    """Verifies result integrity before certification."""

    def __init__(
        self,
        vote_repository: VoteRepository | None = None,
        election_repository: ElectionRepository | None = None,
    ):
        self.vote_repository = vote_repository or VoteRepository()
        self.election_repository = election_repository or ElectionRepository()

    def verify(self, election: Election, *, fraud_acknowledged: bool = False) -> dict:
        checks = {}
        blocking = []

        closed_ok = election.status in {Election.Status.CLOSED, Election.Status.ARCHIVED}
        checks["election_closed"] = {"passed": closed_ok}
        if not closed_ok:
            blocking.append("Election must be closed before results can be certified.")

        hash_check = self.vote_repository.verify_hashes_for_election(election)
        checks["vote_hashes"] = hash_check
        if not hash_check["passed"]:
            blocking.append(f"{hash_check['invalid_count']} vote hash(es) invalid.")

        svt_check = self._verify_svts(election)
        checks["svt_validity"] = svt_check
        if not svt_check["passed"]:
            blocking.append("One or more SVT records are invalid for submitted ballots.")

        duplicate_check = self._verify_no_duplicate_ballots(election)
        checks["duplicate_ballots"] = duplicate_check
        if not duplicate_check["passed"]:
            blocking.append("Duplicate ballot submissions detected.")

        max_votes_check = self.vote_repository.check_max_votes_per_position(election)
        checks["max_votes_rules"] = max_votes_check
        if not max_votes_check["passed"]:
            blocking.append("Votes exceed max_votes_allowed for one or more positions.")

        fraud_check = self._verify_fraud_cases(election, fraud_acknowledged=fraud_acknowledged)
        checks["fraud_cases"] = fraud_check
        if not fraud_check["passed"]:
            blocking.append("Open fraud cases must be resolved or acknowledged.")

        audit_check = self._verify_audit_trail(election)
        checks["audit_trail"] = audit_check
        if not audit_check["passed"]:
            blocking.append("Audit trail incomplete for this election.")

        return {
            "is_valid": len(blocking) == 0,
            "checks": checks,
            "blocking_issues": blocking,
            "verified_at": timezone.now().isoformat(),
        }

    def _verify_svts(self, election: Election) -> dict:
        votes = self.vote_repository.list_for_election(election)
        invalid = []
        for vote in votes:
            if not vote.svt_id:
                invalid.append({"vote_id": str(vote.vote_id), "reason": "missing_svt"})
                continue
            svt = SVTToken.objects.filter(svt_id=vote.svt_id).first()
            if not svt or svt.status != SVTToken.Status.USED:
                invalid.append({"vote_id": str(vote.vote_id), "reason": "svt_not_used"})
        return {"passed": len(invalid) == 0, "invalid_records": invalid[:50]}

    def _verify_no_duplicate_ballots(self, election: Election) -> dict:
        used_svts = (
            SVTToken.objects.filter(election=election, status=SVTToken.Status.USED)
            .values("user_id")
            .annotate(svt_count=Count("svt_id"))
        )
        violations = [
            {"user_id": row["user_id"], "svt_count": row["svt_count"]}
            for row in used_svts
            if row["svt_count"] > 1
        ]
        return {"passed": len(violations) == 0, "violations": violations[:50]}

    def _verify_fraud_cases(self, election: Election, *, fraud_acknowledged: bool) -> dict:
        open_cases = FraudCase.objects.filter(
            election=election,
            status__in=[
                FraudCase.Status.OPEN,
                FraudCase.Status.INVESTIGATING,
                FraudCase.Status.ESCALATED,
            ],
        ).count()
        open_alerts = SecurityAlert.objects.filter(
            election=election,
            status__in=[
                SecurityAlert.Status.OPEN,
                SecurityAlert.Status.REVIEWING,
                SecurityAlert.Status.ESCALATED,
            ],
        ).count()
        passed = (open_cases == 0 and open_alerts == 0) or fraud_acknowledged
        return {
            "passed": passed,
            "open_fraud_cases": open_cases,
            "open_security_alerts": open_alerts,
            "acknowledged": fraud_acknowledged,
        }

    def _verify_audit_trail(self, election: Election) -> dict:
        required = [
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            AuditLog.EventType.BALLOT_SUBMITTED,
        ]
        missing = []
        vote_count = self.vote_repository.count_for_election(election)
        for event_type in required:
            if not AuditLog.objects.filter(election=election, event_type=event_type).exists():
                if event_type == AuditLog.EventType.BALLOT_SUBMITTED and vote_count == 0:
                    continue
                missing.append(event_type)
        return {"passed": len(missing) == 0, "missing_events": missing}


class ResultsGenerationService:
    """Aggregates immutable vote records into certified standings."""

    def __init__(
        self,
        result_repository: ElectionResultRepository | None = None,
        vote_repository: VoteRepository | None = None,
        integrity_service: ResultIntegrityService | None = None,
        election_repository: ElectionRepository | None = None,
    ):
        self.result_repository = result_repository or ElectionResultRepository()
        self.vote_repository = vote_repository or VoteRepository()
        self.integrity_service = integrity_service or ResultIntegrityService()
        self.election_repository = election_repository or ElectionRepository()

    def ensure_pending_result(self, election: Election) -> ElectionResult:
        existing = self.result_repository.get_by_election(election)
        if existing:
            return existing
        return self.result_repository.create(
            election=election,
            status=ElectionResult.Status.PENDING_GENERATION,
        )

    @transaction.atomic
    def auto_generate_on_close(self, election: Election) -> ElectionResult:
        """Generate results automatically when an election closes (Phase 30)."""
        return self.generate_results(election.uuid, actor=None, automated=True)

    @transaction.atomic
    def generate_results(self, election_uuid, actor=None, *, automated: bool = False) -> ElectionResult:
        election = self._get_election(election_uuid)
        try:
            validate_election_closed_for_results(election.status)
        except Exception as exc:
            raise ValidationError(message=str(exc), code="election_not_closed") from exc

        result = self.ensure_pending_result(election)
        if result.status not in {
            ElectionResult.Status.PENDING_GENERATION,
            ElectionResult.Status.GENERATED,
        }:
            raise ConflictError(
                message="Results have already progressed beyond generation.",
                code="result_already_generated",
            )

        standings = self._aggregate_standings(election)
        integrity = self.integrity_service.verify(election)

        eligible = VoterEligibility.objects.filter(election=election, is_eligible=True).count()
        voters = self.vote_repository.count_distinct_voters(election)
        total_votes = self.vote_repository.count_for_election(election)
        turnout = Decimal("0")
        if eligible > 0:
            turnout = (Decimal(voters) / Decimal(eligible) * Decimal("100")).quantize(Decimal("0.01"))

        result_hash = ElectionResult.compute_result_hash(standings)
        new_status = (
            ElectionResult.Status.PENDING_CERTIFICATION
            if integrity["is_valid"]
            else ElectionResult.Status.GENERATED
        )

        result = self.result_repository.update(
            result,
            status=new_status,
            standings=standings,
            integrity_report=integrity,
            turnout_percentage=turnout,
            total_votes_cast=total_votes,
            eligible_voters=eligible,
            result_hash=result_hash,
            generated_at=timezone.now(),
            generated_by=actor,
        )

        action = "results_auto_generated" if automated else "results_generated"
        self._log_audit(actor, election, AuditLog.EventType.ADMIN_ACTION, action)
        self._broadcast_generated(result)
        logger.info(
            "Results %s for election %s (automated=%s)",
            "auto-generated" if automated else "generated",
            election.uuid,
            automated,
        )
        return result

    def _aggregate_standings(self, election: Election) -> dict:
        aggregates = self.vote_repository.aggregate_votes_by_position_candidate(election)
        positions_map: dict = {}

        for row in aggregates:
            pos_uuid = str(row["position__uuid"])
            if pos_uuid not in positions_map:
                positions_map[pos_uuid] = {
                    "position_uuid": pos_uuid,
                    "position_title": row["position__title"],
                    "max_votes_allowed": row["position__max_votes_allowed"],
                    "display_order": row["position__display_order"],
                    "candidates": [],
                    "total_ballots": 0,
                }
            positions_map[pos_uuid]["candidates"].append(
                {
                    "candidate_uuid": str(row["candidate__uuid"]),
                    "full_name": row["candidate__full_name"],
                    "department": row["candidate__department"] or "",
                    "vote_count": row["vote_count"],
                }
            )

        for position in Position.objects.filter(election=election, is_active=True):
            pos_uuid = str(position.uuid)
            if pos_uuid not in positions_map:
                positions_map[pos_uuid] = {
                    "position_uuid": pos_uuid,
                    "position_title": position.title,
                    "max_votes_allowed": position.max_votes_allowed,
                    "display_order": position.display_order,
                    "candidates": [],
                    "total_ballots": 0,
                }

        positions = sorted(positions_map.values(), key=lambda p: p["display_order"])
        for pos in positions:
            total = sum(c["vote_count"] for c in pos["candidates"])
            pos["total_ballots"] = total
            for candidate in pos["candidates"]:
                candidate["vote_percentage"] = (
                    round(candidate["vote_count"] / total * 100, 2) if total else 0.0
                )
            if pos["candidates"]:
                max_votes = max(c["vote_count"] for c in pos["candidates"])
                winners = [c["candidate_uuid"] for c in pos["candidates"] if c["vote_count"] == max_votes and max_votes > 0]
            else:
                winners = []
            pos["winners"] = winners
            for candidate in pos["candidates"]:
                candidate["is_winner"] = candidate["candidate_uuid"] in winners

        eligible = VoterEligibility.objects.filter(election=election, is_eligible=True).count()
        voters = self.vote_repository.count_distinct_voters(election)
        total_votes = self.vote_repository.count_for_election(election)
        turnout = round(voters / eligible * 100, 2) if eligible else 0.0

        return {
            "positions": positions,
            "summary": {
                "eligible_voters": eligible,
                "voters_participated": voters,
                "turnout_percentage": turnout,
                "total_votes_cast": total_votes,
            },
        }

    def _get_election(self, election_uuid) -> Election:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        return election

    def _log_audit(self, user, election, event_type, action: str) -> None:
        AuditLog.objects.create(
            user=user,
            election=election,
            event_type=event_type,
            metadata={"action": action},
        )

    def _broadcast_generated(self, result: ElectionResult) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.results_generated(result)
        except Exception:
            logger.exception("Failed to broadcast results_generated for %s", result.uuid)


results_generation_service = ResultsGenerationService()
result_integrity_service = ResultIntegrityService()
