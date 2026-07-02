import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.validators import (
    validate_election_can_be_deleted,
    validate_election_can_be_opened,
    validate_election_dates,
    validate_election_is_editable,
    validate_status_transition,
)
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class ElectionService:
    """Business logic for election lifecycle management."""

    def __init__(self, repository: ElectionRepository | None = None):
        self.repository = repository or ElectionRepository()

    def list_elections(
        self,
        query: str | None = None,
        status: str | None = None,
        election_type: str | None = None,
    ):
        return self.repository.search(
            query=query,
            status=status,
            election_type=election_type,
        )

    def get_election(self, uuid) -> Election:
        election = self.repository.get_by_uuid(uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        return election

    def create_election(self, created_by, data: dict) -> Election:
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        try:
            validate_election_dates(start_date, end_date)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="invalid_dates") from exc

        election = self.repository.create(created_by=created_by, **data)
        logger.info("Election created: %s", election.uuid)
        return election

    def update_election(self, uuid, data: dict) -> Election:
        election = self.get_election(uuid)
        try:
            validate_election_is_editable(election)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="election_read_only") from exc

        start_date = data.get("start_date", election.start_date)
        end_date = data.get("end_date", election.end_date)
        try:
            validate_election_dates(start_date, end_date)
        except DjangoValidationError as exc:
            raise ValidationError(message=str(exc.message), code="invalid_dates") from exc

        election = self.repository.update(election, **data)
        logger.info("Election updated: %s", election.uuid)
        return election

    def delete_election(self, uuid) -> None:
        election = self.get_election(uuid)
        try:
            validate_election_can_be_deleted(election)
        except DjangoValidationError as exc:
            raise ConflictError(message=str(exc.message), code="election_delete_denied") from exc

        from apps.elections.services.election_purge_service import election_purge_service

        election_purge_service.purge_election(election)
        logger.info("Election deleted: %s", uuid)

    def schedule_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.SCHEDULED)

    def open_election(self, uuid, *, actor=None) -> Election:
        election = self.get_election(uuid)
        from apps.elections.services.election_readiness_service import election_readiness_service

        election_readiness_service.validate_for_open(election, actor=actor)
        return self._transition(uuid, Election.Status.OPEN)

    def pause_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.PAUSED)

    def close_election(self, uuid) -> Election:
        election = self._transition(uuid, Election.Status.CLOSED)
        self._auto_generate_results(election)
        return election

    def _auto_generate_results(self, election: Election) -> None:
        try:
            from apps.results.services.results_service import results_generation_service

            results_generation_service.auto_generate_on_close(election)
        except Exception:
            logger.exception("Automatic results generation failed for election %s", election.uuid)

    def archive_election(self, uuid) -> Election:
        return self._transition(uuid, Election.Status.ARCHIVED)

    def _transition(self, uuid, new_status: str) -> Election:
        election = self.get_election(uuid)
        try:
            validate_status_transition(election.status, new_status)
        except DjangoValidationError as exc:
            raise ValidationError(
                message=str(exc.message),
                code="invalid_status_transition",
            ) from exc

        election = self.repository.update(election, status=new_status)
        logger.info("Election %s transitioned to %s", election.uuid, new_status)
        if new_status == Election.Status.OPEN:
            self._on_election_opened(election)
        self._broadcast_status_change(election, new_status)
        return election

    def _on_election_opened(self, election: Election) -> None:
        try:
            from apps.elections.services.election_pin_service import election_pin_service

            election_pin_service.generate_pins_for_election(election)
        except Exception:
            logger.exception("Election PIN generation failed for %s", election.uuid)

    def _broadcast_status_change(self, election, new_status: str) -> None:
        try:
            from apps.dashboard.services.dashboard_service import dashboard_service
            from core.realtime.broadcasting import realtime_broadcast_service

            if new_status == Election.Status.OPEN:
                realtime_broadcast_service.election_opened(election)
                realtime_broadcast_service.dashboard_stats(
                    role="admin",
                    user_uuid=None,
                    payload=dashboard_service.get_admin_overview(),
                )
            elif new_status == Election.Status.CLOSED:
                realtime_broadcast_service.election_closed(election)
                realtime_broadcast_service.dashboard_stats(
                    role="admin",
                    user_uuid=None,
                    payload=dashboard_service.get_admin_overview(),
                )
        except Exception:
            logger.exception("Failed to broadcast election status change for %s", election.uuid)

    def get_public_campus_status(self) -> dict:
        """Non-sensitive election phase for the public landing page."""
        from apps.results.models import ElectionResult
        from apps.results.repositories.election_result_repository import ElectionResultRepository

        def _serialize(election: Election) -> dict:
            return {
                "uuid": str(election.uuid),
                "title": election.title,
                "status": election.status,
                "start_date": election.start_date,
                "end_date": election.end_date,
            }

        active = (
            self.repository.search(status=Election.Status.OPEN).order_by("-start_date").first()
            or self.repository.search(status=Election.Status.PAUSED).order_by("-start_date").first()
        )
        if active:
            return {"phase": "election_open", "election": _serialize(active)}

        scheduled = self.repository.search(status=Election.Status.SCHEDULED).order_by("start_date").first()
        if scheduled:
            return {"phase": "election_scheduled", "election": _serialize(scheduled)}

        result_repo = ElectionResultRepository()
        pending = (
            result_repo.list_certification_queue()
            .select_related("election")
            .order_by("-created_at")
            .first()
        )
        if pending:
            return {"phase": "awaiting_certification", "election": _serialize(pending.election)}

        published = (
            result_repo.list_filtered(status=ElectionResult.Status.PUBLISHED)
            .order_by("-published_at")
            .first()
        )
        if published:
            return {
                "phase": "results_published",
                "election": _serialize(published.election),
                "published_at": published.published_at,
            }

        return {"phase": "before_election", "election": None}

    def get_public_election_portal(self) -> dict:
        """Public transparency data — no candidate rankings or vote totals while voting is open."""
        from apps.candidates.models import Candidate
        from apps.elections.models import Position
        from apps.results.models import ElectionResult
        from apps.results.repositories.election_result_repository import ElectionResultRepository
        from apps.voting.repositories.vote_repository import VoteRepository

        base = self.get_public_campus_status()
        election_data = base.get("election")
        if not election_data:
            return {
                **base,
                "countdown": None,
                "turnout": None,
                "timeline": [],
                "candidates": [],
                "announcements": [],
                "operational_status": "standby",
            }

        election = self.get_election(election_data["uuid"])
        phase = base["phase"]
        vote_repo = VoteRepository()
        eligible = election.voter_eligibilities.filter(is_eligible=True).count()
        participated = vote_repo.count_distinct_voters(election)
        turnout_pct = round(participated / eligible * 100, 2) if eligible else 0.0

        show_turnout = phase in {
            "election_open",
            "awaiting_certification",
            "results_published",
        } or election.status == Election.Status.CLOSED

        countdown = None
        if phase == "election_scheduled":
            countdown = {
                "label": "Time until voting opens",
                "target_at": election.start_date,
            }
        elif phase == "election_open":
            countdown = {
                "label": "Time until voting closes",
                "target_at": election.end_date,
            }

        timeline = self._build_public_timeline(election, phase, base.get("published_at"))

        positions = Position.objects.filter(election=election, is_active=True).order_by("display_order")
        candidates = []
        for position in positions:
            approved = Candidate.objects.filter(
                election=election,
                position=position,
                status=Candidate.Status.APPROVED,
            ).order_by("full_name")
            candidates.append(
                {
                    "position_uuid": str(position.uuid),
                    "position_title": position.title,
                    "candidates": [
                        {
                            "uuid": str(c.uuid),
                            "full_name": c.full_name,
                            "department": c.department or "",
                            "manifesto_excerpt": (c.manifesto or "")[:280],
                        }
                        for c in approved
                    ],
                }
            )

        announcements = self._build_public_announcements(election, phase, base.get("published_at"))

        result = ElectionResultRepository().get_by_election(election)
        operational_status = "nominal"
        if phase == "election_open" and result and result.integrity_report:
            if not result.integrity_report.get("is_valid", True):
                operational_status = "monitoring"

        return {
            **base,
            "countdown": countdown,
            "turnout": (
                {
                    "percentage": turnout_pct,
                    "participated": participated,
                    "eligible": eligible,
                }
                if show_turnout
                else None
            ),
            "timeline": timeline,
            "candidates": candidates,
            "announcements": announcements,
            "operational_status": operational_status,
            "result_status": result.status if result else None,
        }

    def _build_public_timeline(self, election: Election, phase: str, published_at) -> list[dict]:
        steps = [
            {
                "key": "scheduled",
                "label": "Election scheduled",
                "at": election.start_date,
            },
            {
                "key": "open",
                "label": "Voting opens",
                "at": election.start_date,
            },
            {
                "key": "close",
                "label": "Voting closes",
                "at": election.end_date,
            },
            {
                "key": "certification",
                "label": "Results certification",
                "at": None,
            },
            {
                "key": "published",
                "label": "Results published",
                "at": published_at,
            },
        ]

        phase_order = {
            "before_election": 0,
            "election_scheduled": 1,
            "election_open": 2,
            "awaiting_certification": 3,
            "results_published": 4,
        }
        current_idx = phase_order.get(phase, 0)

        timeline = []
        for idx, step in enumerate(steps):
            if idx < current_idx:
                state = "completed"
            elif idx == current_idx:
                state = "current"
            else:
                state = "upcoming"
            timeline.append({**step, "state": state, "at": step["at"]})
        return timeline

    def _build_public_announcements(self, election: Election, phase: str, published_at) -> list[dict]:
        messages = {
            "election_scheduled": "The election schedule has been published. Voting will open at the time shown below.",
            "election_open": "Voting is now open. Sign in with your index number or email to cast your ballot.",
            "awaiting_certification": "Voting has closed. Results have been generated and await certification by the Electoral Commission.",
            "results_published": "Official results have been certified and published.",
        }
        body = messages.get(phase)
        if not body:
            return []
        return [
            {
                "title": election.title,
                "body": body,
                "at": published_at or election.updated_at,
            }
        ]
