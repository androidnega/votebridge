import hashlib
import logging

from django.db import transaction
from django.utils import timezone

from apps.security.models import SVTToken
from apps.strongroom.models import BallotSeal, ElectionSeal
from apps.strongroom.repositories.strongroom_repository import (
    BallotSealRepository,
    ElectionSealRepository,
)
from apps.strongroom.services.custody_service import custody_service
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class StrongroomService:
    """Seals ballots using immutable vote references — no vote duplication."""

    def __init__(
        self,
        ballot_repository: BallotSealRepository | None = None,
        vote_repository: VoteRepository | None = None,
    ):
        self.ballot_repository = ballot_repository or BallotSealRepository()
        self.vote_repository = vote_repository or VoteRepository()

    @transaction.atomic
    def seal_ballot_for_svt(self, svt: SVTToken) -> BallotSeal | None:
        if svt.status != SVTToken.Status.USED:
            return None

        existing = self.ballot_repository.get_by_svt(svt.election, svt.user, svt.svt_id)
        if existing:
            return existing

        votes = list(self.vote_repository.list_by_svt_id(svt.svt_id))
        if not votes:
            logger.warning("No votes found for consumed SVT %s", svt.svt_id)
            return None

        vote_refs = [str(v.vote_id) for v in votes]
        vote_hashes = [v.vote_hash for v in votes]
        seal_hash = BallotSeal.compute_seal_hash(
            svt.election.uuid, svt.svt_id, vote_refs, vote_hashes
        )

        previous = {"status": "unsealed"}
        seal = self.ballot_repository.create(
            election=svt.election,
            user=svt.user,
            svt_id=svt.svt_id,
            vote_references=vote_refs,
            seal_hash=seal_hash,
            vote_count=len(vote_refs),
            status=BallotSeal.Status.SEALED,
            sealed_at=timezone.now(),
        )

        custody_service.record(
            election=svt.election,
            action="strongroom_sealed",
            actor=svt.user,
            entity_type="ballot_seal",
            entity_uuid=seal.uuid,
            previous_state=previous,
            current_state={
                "status": seal.status,
                "seal_hash": seal_hash,
                "vote_count": len(vote_refs),
                "svt_id": str(svt.svt_id),
            },
            metadata={"vote_references": vote_refs},
        )
        self._broadcast_sealed(seal)
        logger.info("Ballot sealed: %s (%s votes)", seal.uuid, seal.vote_count)
        return seal

    def verify_ballot_seal(self, seal: BallotSeal) -> dict:
        votes = Vote.objects.filter(vote_id__in=seal.vote_references)
        vote_map = {str(v.vote_id): v for v in votes}
        missing = [ref for ref in seal.vote_references if ref not in vote_map]
        hash_mismatch = []
        for ref in seal.vote_references:
            vote = vote_map.get(ref)
            if not vote:
                continue
            expected = Vote.compute_vote_hash(
                election_id=vote.election_id,
                position_id=vote.position_id,
                candidate_id=vote.candidate_id,
                user_id=vote.user_id,
                channel_id=vote.channel_id,
                timestamp_iso=vote.timestamp.isoformat(),
            )
            if vote.vote_hash != expected:
                hash_mismatch.append(ref)

        recomputed = BallotSeal.compute_seal_hash(
            seal.election.uuid,
            seal.svt_id,
            seal.vote_references,
            [vote_map[r].vote_hash for r in seal.vote_references if r in vote_map],
        )
        seal_valid = seal.seal_hash == recomputed and not missing and not hash_mismatch

        return {
            "passed": seal_valid,
            "seal_hash_valid": seal.seal_hash == recomputed,
            "missing_votes": missing,
            "hash_mismatches": hash_mismatch,
            "vote_count": seal.vote_count,
        }

    def verify_all_ballot_seals(self, election) -> dict:
        seals = self.ballot_repository.list_for_election(election)
        results = []
        failed = 0
        for seal in seals:
            check = self.verify_ballot_seal(seal)
            results.append({"seal_uuid": str(seal.uuid), **check})
            if not check["passed"]:
                failed += 1
        return {
            "passed": failed == 0,
            "total_seals": len(results),
            "failed_seals": failed,
            "details": results[:50],
        }

    @staticmethod
    def compute_ballot_seals_digest(election) -> str:
        hashes = list(
            BallotSeal.objects.filter(election=election)
            .order_by("sealed_at")
            .values_list("seal_hash", flat=True)
        )
        payload = "|".join(hashes)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _broadcast_sealed(self, seal: BallotSeal) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.strongroom_sealed(seal)
        except Exception:
            logger.exception("Failed to broadcast strongroom_sealed for %s", seal.uuid)


class ElectionSealService:
    """Creates and manages election-level cryptographic seals."""

    def __init__(
        self,
        election_seal_repository: ElectionSealRepository | None = None,
        strongroom_service: StrongroomService | None = None,
    ):
        self.repository = election_seal_repository or ElectionSealRepository()
        self.strongroom = strongroom_service or StrongroomService()

    @transaction.atomic
    def seal_on_certification(self, election_result, actor=None) -> ElectionSeal:
        election = election_result.election
        existing = self.repository.get_by_election(election)
        if existing and existing.status in {ElectionSeal.Status.SEALED, ElectionSeal.Status.LOCKED}:
            return existing

        ballot_digest = StrongroomService.compute_ballot_seals_digest(election)
        certified_at = election_result.certified_at or timezone.now()
        seal_hash = ElectionSeal.compute_election_seal_hash(
            election.uuid,
            election_result.result_hash,
            ballot_digest,
            certified_at.isoformat(),
        )
        verification_hash = ElectionSeal.compute_verification_hash(election.uuid, seal_hash)

        previous = {"status": existing.status if existing else "none"}
        if existing:
            seal = self.repository.update(
                existing,
                election_result=election_result,
                election_seal_hash=seal_hash,
                verification_hash=verification_hash,
                ballot_seals_digest=ballot_digest,
                status=ElectionSeal.Status.SEALED,
                sealed_at=certified_at,
                sealed_by=actor or election_result.certified_by,
            )
        else:
            seal = self.repository.create(
                election=election,
                election_result=election_result,
                election_seal_hash=seal_hash,
                verification_hash=verification_hash,
                ballot_seals_digest=ballot_digest,
                status=ElectionSeal.Status.SEALED,
                sealed_at=certified_at,
                sealed_by=actor or election_result.certified_by,
            )

        custody_service.record(
            election=election,
            action="election_sealed",
            actor=actor or election_result.certified_by,
            entity_type="election_seal",
            entity_uuid=seal.uuid,
            previous_state=previous,
            current_state={
                "status": seal.status,
                "election_seal_hash": seal_hash,
                "verification_hash": verification_hash,
            },
        )
        logger.info("Election sealed: %s", election.uuid)
        return seal

    @transaction.atomic
    def lock_election(self, election, actor=None) -> ElectionSeal:
        seal = self.repository.get_by_election(election)
        if not seal:
            raise NotFoundError(message="Election seal not found.", code="seal_not_found")
        if seal.status == ElectionSeal.Status.LOCKED:
            return seal

        previous = {"status": seal.status}
        seal = self.repository.update(
            seal,
            status=ElectionSeal.Status.LOCKED,
            locked_at=timezone.now(),
            locked_by=actor,
        )
        custody_service.record(
            election=election,
            action="election_locked",
            actor=actor,
            entity_type="election_seal",
            entity_uuid=seal.uuid,
            previous_state=previous,
            current_state={"status": seal.status},
        )
        self._broadcast_locked(seal)
        return seal

    def verify_election_seal(self, seal: ElectionSeal) -> dict:
        if not seal.election_result:
            return {"passed": False, "reason": "no_linked_result"}

        result = seal.election_result
        ballot_digest = StrongroomService.compute_ballot_seals_digest(seal.election)
        certified_at = result.certified_at.isoformat() if result.certified_at else ""
        expected = ElectionSeal.compute_election_seal_hash(
            seal.election.uuid,
            result.result_hash,
            ballot_digest,
            certified_at,
        )
        verification_expected = ElectionSeal.compute_verification_hash(
            seal.election.uuid, expected
        )

        return {
            "passed": seal.election_seal_hash == expected
            and seal.verification_hash == verification_expected
            and seal.ballot_seals_digest == ballot_digest,
            "seal_hash_valid": seal.election_seal_hash == expected,
            "verification_hash_valid": seal.verification_hash == verification_expected,
            "ballot_digest_valid": seal.ballot_seals_digest == ballot_digest,
        }

    def _broadcast_locked(self, seal: ElectionSeal) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            realtime_broadcast_service.election_locked(seal)
        except Exception:
            logger.exception("Failed to broadcast election_locked for %s", seal.election.uuid)


strongroom_service = StrongroomService()
election_seal_service = ElectionSealService()
