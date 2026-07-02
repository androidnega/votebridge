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
from apps.security.repositories.svt_repository import SVTRepository
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
        svt_repository: SVTRepository | None = None,
    ):
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.position_repository = position_repository or PositionRepository()
        self.candidate_repository = candidate_repository or CandidateRepository()
        self.vote_repository = vote_repository or VoteRepository()
        self.audit_service = audit_service or VoteAuditService()
        self.svt_repository = svt_repository or SVTRepository()

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
                            "image_url": c.image.url if c.image else None,
                        }
                        for c in candidates
                    ],
                }
            )

        self.audit_service.log_ballot_viewed(user, election, ip_address, user_agent)

        active_svt = self.svt_repository.get_active_svt_for_user_election(user, election)
        from apps.security.models import SVTToken
        from apps.voting.services.presence_service import pre_vote_presence_service
        from core.utils.phone import mask_phone_number

        if active_svt and active_svt.status == SVTToken.Status.VALIDATED:
            pre_vote_presence_service.ensure_presence_for_web_ballot(user, election, active_svt)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "status": election.status,
            "positions": ballot_positions,
            "svt_status": active_svt.status if active_svt else None,
            "can_request_svt": active_svt is None,
            "masked_phone": mask_phone_number(user.phone_number),
            "validated_at": active_svt.validated_at if active_svt else None,
            "ballot_session_active": bool(
                active_svt and active_svt.status == SVTToken.Status.VALIDATED
            ),
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
                message="Your ballot payload is empty.",
                code="empty_ballot",
            )

        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        svt = self.svt_service.get_svt_for_submit(token_code, user, election_uuid)

        if channel_name == "web":
            from apps.voting.services.presence_service import pre_vote_presence_service

            pre_vote_presence_service.ensure_presence_for_web_ballot(user, election, svt)

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
        positions_with_selection = 0

        for selection in selections:
            position_uuid = str(selection["position_uuid"])
            candidate_uuids = selection.get("candidate_uuids") or []

            if not candidate_uuids:
                continue

            positions_with_selection += 1
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
            if existing_count >= position.max_votes_allowed:
                if position.title not in positions_completed:
                    positions_completed.append(position.title)
                continue

            pending_uuids = []
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
                    continue

                pending_uuids.append(candidate_uuid)

            if not pending_uuids:
                if position.title not in positions_completed and existing_count > 0:
                    positions_completed.append(position.title)
                continue

            if existing_count + len(pending_uuids) > position.max_votes_allowed:
                raise ConflictError(
                    message=f"Maximum votes reached for {position.title}.",
                    code="max_votes_reached",
                )

            position_voted = False
            for candidate_uuid in pending_uuids:
                candidate = self.candidate_repository.get_by_uuid(candidate_uuid)

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
            if not positions_completed:
                raise ValidationError(
                    message="Select at least one candidate before submitting your ballot.",
                    code="empty_ballot",
                )

        total_votes = self.vote_repository.get_queryset().filter(
            user=user,
            election=election,
        ).count()

        self.svt_service.consume_svt(
            svt,
            user,
            vote_count=len(created_votes) or total_votes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        confirmation_reference = self._build_confirmation_reference(svt)
        positions_skipped = max(0, len(eligible_positions) - len(positions_completed))

        result = {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "confirmation_reference": confirmation_reference,
            "positions_completed": positions_completed,
            "positions_count": len(positions_completed),
            "positions_skipped": positions_skipped,
            "votes_count": len(created_votes) or total_votes,
            "timestamp": created_votes[-1].timestamp if created_votes else timezone.now(),
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
            if election.status in {election.Status.OPEN, election.Status.PAUSED}:
                from apps.analytics.services.election_live_trend_service import (
                    election_live_trend_service,
                )

                live_trend = election_live_trend_service.build_snapshot(election)
                realtime_broadcast_service.live_trend_updated(
                    election=election,
                    live_trend=live_trend,
                )
        except Exception:
            logger.exception("Failed to broadcast ballot submission for election %s", election.uuid)

    @staticmethod
    def _build_confirmation_reference(svt) -> str:
        year = timezone.now().year
        suffix = int(str(svt.svt_id).replace("-", "")[:8], 16) % 1_000_000
        return f"VTB-{year}-{suffix:06d}"

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
