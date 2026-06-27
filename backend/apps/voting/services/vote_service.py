import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MFALog
from apps.accounts.services.mfa_service import MFAService
from apps.candidates.models import Candidate
from apps.candidates.repositories.candidate_repository import CandidateRepository
from apps.elections.models import Election, VotingChannel
from apps.elections.repositories.election_repository import (
    ElectionRepository,
    VotingChannelRepository,
)
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.elections.repositories.position_repository import PositionRepository
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository
from apps.voting.validators import (
    validate_candidate_for_ballot,
    validate_channel_active,
    validate_channel_allowed_for_election,
    validate_election_is_open,
)
from apps.security.services.svt_service import SVTService
from core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")


class VoteAuditService:
    """Writes vote lifecycle events to the existing MFALog audit table."""

    def __init__(self, mfa_service: MFAService | None = None):
        self.mfa_service = mfa_service or MFAService()

    def log_ballot_viewed(self, user, election, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.BALLOT_VIEWED,
            user,
            election,
            ip_address,
            user_agent,
        )

    def log_vote_cast(self, user, vote: Vote, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.VOTE_CAST,
            user,
            vote.election,
            ip_address,
            user_agent,
            {
                "vote_id": str(vote.vote_id),
                "position_id": str(vote.position.uuid),
                "candidate_id": str(vote.candidate.uuid),
                "channel": vote.channel.channel_name,
            },
        )

    def log_vote_verified(self, user, vote: Vote, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.VOTE_VERIFIED,
            user,
            vote.election,
            ip_address,
            user_agent,
            {"vote_id": str(vote.vote_id), "vote_hash": vote.vote_hash},
        )

    def log_confirmation_viewed(self, user, vote: Vote, ip_address=None, user_agent=None):
        return self._log(
            MFALog.EventType.VOTE_CONFIRMATION_VIEWED,
            user,
            vote.election,
            ip_address,
            user_agent,
            {"vote_id": str(vote.vote_id)},
        )

    def _log(self, event_type, user, election, ip_address, user_agent, metadata=None):
        return self.mfa_service.log(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "election_uuid": str(election.uuid),
                **(metadata or {}),
            },
        )


class BallotService:
    """Builds voter-facing ballots from existing election data."""

    def __init__(
        self,
        election_repository: ElectionRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
        position_repository: PositionRepository | None = None,
        candidate_repository: CandidateRepository | None = None,
        vote_repository: VoteRepository | None = None,
        audit_service: VoteAuditService | None = None,
    ):
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.position_repository = position_repository or PositionRepository()
        self.candidate_repository = candidate_repository or CandidateRepository()
        self.vote_repository = vote_repository or VoteRepository()
        self.audit_service = audit_service or VoteAuditService()

    def get_ballot(self, election_uuid, user, ip_address=None, user_agent=None) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        try:
            validate_election_is_open(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="election_not_open") from exc

        if not self.eligibility_repository.is_user_eligible(election, user):
            raise PermissionDeniedError(
                message="You are not eligible to vote in this election.",
                code="not_eligible",
            )

        positions = self.eligibility_repository.get_eligible_positions_for_user(
            election, user
        ).prefetch_related("candidates")

        ballot_positions = []
        for position in positions:
            candidates = position.candidates.filter(status=Candidate.Status.APPROVED)
            user_votes = self.vote_repository.list_for_user_position(user, position)
            voted_candidate_ids = {v.candidate_id for v in user_votes}
            votes_cast = user_votes.count()

            ballot_positions.append(
                {
                    "uuid": str(position.uuid),
                    "title": position.title,
                    "description": position.description,
                    "max_votes_allowed": position.max_votes_allowed,
                    "choice_type": "single" if position.is_single_choice else "multi",
                    "display_order": position.display_order,
                    "votes_cast": votes_cast,
                    "votes_remaining": max(0, position.max_votes_allowed - votes_cast),
                    "candidates": [
                        {
                            "uuid": str(c.uuid),
                            "full_name": c.full_name,
                            "department": c.department,
                            "manifesto": c.manifesto,
                            "has_voted": c.id in voted_candidate_ids,
                        }
                        for c in candidates
                    ],
                }
            )

        self.audit_service.log_ballot_viewed(user, election, ip_address, user_agent)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "status": election.status,
            "positions": ballot_positions,
        }


class VoteService:
    """Cast and verify votes."""

    def __init__(
        self,
        vote_repository: VoteRepository | None = None,
        election_repository: ElectionRepository | None = None,
        position_repository: PositionRepository | None = None,
        candidate_repository: CandidateRepository | None = None,
        channel_repository: VotingChannelRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
        audit_service: VoteAuditService | None = None,
        svt_service: SVTService | None = None,
    ):
        self.vote_repository = vote_repository or VoteRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.position_repository = position_repository or PositionRepository()
        self.candidate_repository = candidate_repository or CandidateRepository()
        self.channel_repository = channel_repository or VotingChannelRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.audit_service = audit_service or VoteAuditService()
        self.svt_service = svt_service or SVTService()

    @transaction.atomic
    def submit_ballot(
        self,
        election_uuid,
        user,
        token_code: str,
        selections: list[dict],
        channel_name: str,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        """Submit all ballot selections under one SVT; consume token after all votes recorded."""
        if not selections:
            raise ValidationError(
                message="At least one position selection is required.",
                code="empty_ballot",
            )

        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        svt = self.svt_service.get_svt_for_submit(token_code, user, election_uuid)

        channel = self.channel_repository.get_by_name(channel_name)
        if not channel:
            raise NotFoundError(message="Voting channel not found.", code="channel_not_found")

        try:
            validate_election_is_open(election)
            validate_channel_active(channel)
            validate_channel_allowed_for_election(election, channel)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc), code="vote_validation") from exc

        if not self.eligibility_repository.is_user_eligible(election, user):
            raise PermissionDeniedError(
                message="You are not eligible to vote in this election.",
                code="not_eligible",
            )

        eligible_positions = {
            str(p.uuid): p
            for p in self.eligibility_repository.get_eligible_positions_for_user(election, user)
        }

        created_votes = []
        positions_completed = []

        for selection in selections:
            position_uuid = str(selection["position_uuid"])
            candidate_uuids = selection.get("candidate_uuids") or []

            if not candidate_uuids:
                continue

            position = eligible_positions.get(position_uuid)
            if not position:
                position = self.position_repository.get_by_uuid(position_uuid)
                if not position:
                    raise NotFoundError(message="Position not found.", code="position_not_found")
                raise PermissionDeniedError(
                    message="You are not eligible to vote for this position.",
                    code="position_not_eligible",
                )

            if len(candidate_uuids) > position.max_votes_allowed:
                raise ValidationError(
                    message=f"Too many selections for {position.title}.",
                    code="max_votes_exceeded",
                )

            existing_count = self.vote_repository.count_for_user_position(user, position)
            if existing_count + len(candidate_uuids) > position.max_votes_allowed:
                raise ConflictError(
                    message=f"Maximum votes reached for {position.title}.",
                    code="max_votes_reached",
                )

            position_voted = False
            for candidate_uuid in candidate_uuids:
                candidate = self.candidate_repository.get_by_uuid(candidate_uuid)
                if not candidate:
                    raise NotFoundError(message="Candidate not found.", code="candidate_not_found")

                try:
                    validate_candidate_for_ballot(candidate, position, election)
                except DjangoValidationError as exc:
                    raise ValidationError(message=str(exc), code="vote_validation") from exc

                if self.vote_repository.has_vote_for_user_position_candidate(
                    user, position, candidate
                ):
                    raise ConflictError(
                        message=f"You have already voted for {candidate.full_name}.",
                        code="already_voted_candidate",
                    )

                timestamp = timezone.now()
                vote_hash = Vote.compute_vote_hash(
                    election_id=election.pk,
                    position_id=position.pk,
                    candidate_id=candidate.pk,
                    user_id=user.pk,
                    channel_id=channel.pk,
                    timestamp_iso=timestamp.isoformat(),
                )

                vote = self.vote_repository.create(
                    election=election,
                    position=position,
                    candidate=candidate,
                    user=user,
                    channel=channel,
                    vote_hash=vote_hash,
                    svt_id=svt.svt_id,
                    timestamp=timestamp,
                )
                created_votes.append(vote)
                position_voted = True
                self.audit_service.log_vote_cast(user, vote, ip_address, user_agent)
                logger.info("Vote cast: %s by user %s (ballot submit)", vote.vote_id, user.uuid)

            if position_voted and position.title not in positions_completed:
                positions_completed.append(position.title)

        if not created_votes:
            raise ValidationError(
                message="No valid selections to record.",
                code="empty_ballot",
            )

        self.svt_service.consume_svt(
            svt,
            user,
            vote_count=len(created_votes),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        result = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "positions_completed": positions_completed,
            "positions_count": len(positions_completed),
            "votes_count": len(created_votes),
            "timestamp": created_votes[-1].timestamp,
            "message": "Your vote has been recorded successfully.",
        }
        self._broadcast_ballot_submitted(
            election=election,
            user=user,
            positions_completed=positions_completed,
            positions_count=len(positions_completed),
            votes_count=len(created_votes),
        )
        return result

    def _broadcast_ballot_submitted(
        self,
        *,
        election,
        user,
        positions_completed,
        positions_count,
        votes_count,
    ) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            admin_stats = dashboard_service.get_admin_overview()
            election_stats = dashboard_service.get_election_monitoring(str(election.uuid))
            admin_stats.update(
                {
                    "election_uuid": str(election.uuid),
                    "election_total_votes_cast": election_stats.get("total_votes_cast"),
                    "election_turnout_percentage": election_stats.get("turnout_percentage"),
                }
            )
            student_stats = dashboard_service.get_student_overview(user)
            realtime_broadcast_service.ballot_submitted(
                election=election,
                user=user,
                positions_completed=positions_completed,
                positions_count=positions_count,
                votes_count=votes_count,
                admin_stats=admin_stats,
                student_stats=student_stats,
            )
        except Exception:
            logger.exception("Failed to broadcast ballot submission for election %s", election.uuid)

    def verify_vote(self, vote_id, user, ip_address=None, user_agent=None) -> dict:
        vote = self.vote_repository.get_by_vote_id(vote_id)
        if not vote:
            raise NotFoundError(message="Vote not found.", code="vote_not_found")

        if vote.user_id != user.id:
            raise PermissionDeniedError(
                message="You can only verify your own votes.",
                code="vote_access_denied",
            )

        expected_hash = Vote.compute_vote_hash(
            election_id=vote.election_id,
            position_id=vote.position_id,
            candidate_id=vote.candidate_id,
            user_id=vote.user_id,
            channel_id=vote.channel_id,
            timestamp_iso=vote.timestamp.isoformat(),
        )
        is_valid = vote.vote_hash == expected_hash

        self.audit_service.log_vote_verified(user, vote, ip_address, user_agent)

        return {
            "is_valid": is_valid,
            "election_uuid": str(vote.election.uuid),
            "position_title": vote.position.title,
            "candidate_name": vote.candidate.full_name,
            "channel": vote.channel.channel_name,
            "timestamp": vote.timestamp,
        }

    def get_confirmation(self, vote_id, user, ip_address=None, user_agent=None) -> dict:
        vote = self.vote_repository.get_by_vote_id(vote_id)
        if not vote:
            raise NotFoundError(message="Vote not found.", code="vote_not_found")

        if vote.user_id != user.id:
            raise PermissionDeniedError(
                message="You can only view your own vote confirmations.",
                code="vote_access_denied",
            )

        self.audit_service.log_confirmation_viewed(user, vote, ip_address, user_agent)

        return {
            "election_uuid": str(vote.election.uuid),
            "election_title": vote.election.title,
            "position_title": vote.position.title,
            "candidate_name": vote.candidate.full_name,
            "channel": vote.channel.get_channel_name_display(),
            "timestamp": vote.timestamp,
            "message": "Your vote has been recorded successfully.",
        }

    def list_my_votes(self, election_uuid, user):
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        votes = self.vote_repository.list_for_user_in_election(user, election)
        return votes
