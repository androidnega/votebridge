import logging

from apps.elections.repositories.election_repository import ElectionRepository
from apps.results.models import ElectionResult
from apps.strongroom.models import ElectionSeal, IntegrityVerification
from apps.strongroom.repositories.strongroom_repository import (
    ElectionSealRepository,
    IntegrityVerificationRepository,
)
from apps.strongroom.services.custody_service import custody_service
from apps.strongroom.services.strongroom_service import (
    election_seal_service,
    strongroom_service,
)
from apps.voting.repositories.vote_repository import VoteRepository
from core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class IntegrityVerificationService:
    """Composes existing integrity checks with strongroom verification."""

    def __init__(
        self,
        vote_repository: VoteRepository | None = None,
        election_repository: ElectionRepository | None = None,
        verification_repository: IntegrityVerificationRepository | None = None,
        election_seal_repository: ElectionSealRepository | None = None,
    ):
        self.vote_repository = vote_repository or VoteRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.verification_repository = verification_repository or IntegrityVerificationRepository()
        self.election_seal_repository = election_seal_repository or ElectionSealRepository()

    def verify_full(self, election_uuid, actor=None) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        checks = {}
        blocking = []

        vote_hash_check = self.vote_repository.verify_hashes_for_election(election)
        checks["vote_hashes"] = vote_hash_check
        if not vote_hash_check["passed"]:
            blocking.append("Vote hash verification failed.")

        result_check = self._verify_result_hash(election)
        checks["result_hash"] = result_check
        if not result_check["passed"]:
            blocking.append(result_check.get("reason", "Result hash invalid."))

        ballot_check = strongroom_service.verify_all_ballot_seals(election)
        checks["strongroom_seals"] = ballot_check
        if not ballot_check["passed"]:
            blocking.append("One or more ballot seals are invalid.")

        election_seal = self.election_seal_repository.get_by_election(election)
        if election_seal:
            seal_check = election_seal_service.verify_election_seal(election_seal)
        else:
            seal_check = {"passed": False, "reason": "election_not_sealed"}
        checks["election_seal"] = seal_check
        if not seal_check["passed"]:
            blocking.append("Election seal verification failed.")

        custody_check = custody_service.verify_chain_consistency(election)
        checks["chain_of_custody"] = custody_check
        if not custody_check["passed"]:
            blocking.append("Chain of custody inconsistencies detected.")

        is_valid = len(blocking) == 0
        score = self._compute_score(checks)

        report = {
            "is_valid": is_valid,
            "integrity_score": score,
            "checks": checks,
            "blocking_issues": blocking,
        }

        verification = self.verification_repository.create(
            election=election,
            verification_type=IntegrityVerification.VerificationType.FULL,
            is_valid=is_valid,
            integrity_score=score,
            report=report,
            verified_by=actor,
        )
        self._broadcast_completed(election, verification)
        return {**report, "verification_uuid": str(verification.uuid)}

    def verify_public(self, election_uuid, verification_hash: str) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        seal = self.election_seal_repository.get_by_election(election)
        if not seal or seal.verification_hash != verification_hash:
            raise ValidationError(
                message="Verification hash does not match.",
                code="verification_failed",
            )

        result = getattr(election, "result", None)
        if not result or result.status != ElectionResult.Status.PUBLISHED:
            raise ValidationError(
                message="Results are not published for public verification.",
                code="not_published",
            )

        seal_check = election_seal_service.verify_election_seal(seal)
        is_valid = seal_check.get("passed", False)
        score = 100 if is_valid else 0

        report = {
            "is_valid": is_valid,
            "integrity_score": score,
            "election_title": election.title,
            "election_uuid": str(election.uuid),
            "seal_status": seal.status,
            "sealed_at": seal.sealed_at.isoformat() if seal.sealed_at else None,
            "published_at": result.published_at.isoformat() if result.published_at else None,
            "checks": {"election_seal": seal_check},
        }

        verification = self.verification_repository.create(
            election=election,
            verification_type=IntegrityVerification.VerificationType.PUBLIC,
            is_valid=is_valid,
            integrity_score=score,
            report=report,
            verification_hash_used=verification_hash,
        )
        self._broadcast_verified(election, verification)
        return report

    def _verify_result_hash(self, election) -> dict:
        result = getattr(election, "result", None)
        if not result or not result.result_hash:
            return {"passed": False, "reason": "no_result_hash"}

        from apps.results.models import ElectionResult

        recomputed = ElectionResult.compute_result_hash(result.standings)
        return {
            "passed": result.result_hash == recomputed,
            "stored_hash": result.result_hash,
            "recomputed_hash": recomputed,
        }

    def _compute_score(self, checks: dict) -> int:
        if not checks:
            return 0
        passed = sum(1 for check in checks.values() if check.get("passed"))
        return int(round(passed / len(checks) * 100))

    def get_dashboard(self, election_uuid) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        seal = self.election_seal_repository.get_by_election(election)
        ballot_seals = strongroom_service.ballot_repository.list_for_election(election)
        verifications = list(self.verification_repository.list_for_election(election))
        custody = custody_service.list_timeline(election)

        latest = verifications[0] if verifications else None
        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "seal_status": seal.status if seal else ElectionSeal.Status.PENDING,
            "election_seal_hash": seal.election_seal_hash if seal else "",
            "verification_hash": seal.verification_hash if seal else "",
            "sealed_at": seal.sealed_at.isoformat() if seal and seal.sealed_at else None,
            "locked_at": seal.locked_at.isoformat() if seal and seal.locked_at else None,
            "ballot_seals_count": ballot_seals.count(),
            "integrity_score": latest.integrity_score if latest else None,
            "last_verified_at": latest.verified_at.isoformat() if latest else None,
            "verification_history": [
                {
                    "uuid": str(v.uuid),
                    "verification_type": v.verification_type,
                    "is_valid": v.is_valid,
                    "integrity_score": v.integrity_score,
                    "verified_at": v.verified_at.isoformat(),
                }
                for v in verifications
            ],
            "custody_timeline": [
                {
                    "uuid": str(c.uuid),
                    "action": c.action,
                    "actor_name": c.actor.get_full_name() if c.actor else "System",
                    "previous_state": c.previous_state,
                    "current_state": c.current_state,
                    "timestamp": c.timestamp.isoformat(),
                }
                for c in custody
            ],
        }

    def _broadcast_completed(self, election, verification) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.integrity_check_completed(election, verification)
        except Exception:
            logger.exception("Failed to broadcast integrity_check_completed")

    def _broadcast_verified(self, election, verification) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.strongroom_verified(election, verification)
        except Exception:
            logger.exception("Failed to broadcast strongroom_verified")


integrity_verification_service = IntegrityVerificationService()
