"""Internal live candidate performance for open elections — admin/super-admin only."""

from django.utils import timezone

from apps.analytics.repositories.election_analytics_repository import ElectionAnalyticsRepository
from apps.dashboard.services.dashboard_service import dashboard_service
from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from core.exceptions import NotFoundError, ValidationError

LIVE_STATUSES = {Election.Status.OPEN, Election.Status.PAUSED}


class ElectionLiveTrendService:
    def __init__(
        self,
        repository: ElectionAnalyticsRepository | None = None,
        election_repository: ElectionRepository | None = None,
    ):
        self.repository = repository or ElectionAnalyticsRepository()
        self.election_repository = election_repository or ElectionRepository()

    def get_live_trend(self, election_uuid) -> dict:
        election = self._get_live_election(election_uuid)
        return self.build_snapshot(election)

    def build_snapshot(self, election: Election) -> dict:
        aggregates = self.repository.aggregate_position_candidate_votes(election)
        positions = self._build_positions(aggregates)
        counts = self.repository.election_counts(election)
        monitor = dashboard_service.get_election_monitoring(str(election.uuid)) or {}

        highlights = self._build_highlights(positions)
        active_positions = sum(1 for position in positions if position["total_votes"] > 0)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "last_updated": timezone.now().isoformat(),
            "summary": {
                "turnout_percent": monitor.get("turnout_percentage", 0.0),
                "ballots_submitted": counts["ballots_submitted"],
                "eligible_voters": counts["eligible_voters"],
                "total_votes_cast": counts["total_votes_cast"],
                "positions_total": counts["positions"],
                "positions_active": active_positions,
                "candidates_total": counts["candidates"],
                "closest_race": highlights["closest_race"],
                "leading_by_position": highlights["leading_by_position"],
            },
            "positions": positions,
            "highlights": {
                "top_trending": highlights["top_trending"],
                "closest_races": highlights["closest_races"],
                "highest_turnout_position": highlights["highest_turnout_position"],
            },
            "charts": {
                "hourly_votes": self.repository.vote_hourly_buckets(election),
                "cumulative_ballots": self.repository.cumulative_ballot_timeline(election),
            },
        }

    def _get_live_election(self, election_uuid) -> Election:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        if election.status not in LIVE_STATUSES:
            raise ValidationError(
                message="Live trend is only available while an election is open or paused.",
                code="election_not_live",
            )
        return election

    def _build_positions(self, aggregates: list[dict]) -> list[dict]:
        positions_map: dict[str, dict] = {}

        for row in aggregates:
            pos_uuid = str(row["position__uuid"])
            if pos_uuid not in positions_map:
                positions_map[pos_uuid] = {
                    "position_uuid": pos_uuid,
                    "position_title": row["position__title"],
                    "display_order": row["position__display_order"] or 0,
                    "max_votes_allowed": row["position__max_votes_allowed"],
                    "candidates": [],
                    "total_votes": 0,
                }
            positions_map[pos_uuid]["candidates"].append(
                {
                    "candidate_uuid": str(row["candidate__uuid"]),
                    "full_name": row["candidate__full_name"],
                    "department": row["candidate__department"] or "",
                    "image_path": row["candidate__image"] or "",
                    "vote_count": row["vote_count"],
                }
            )

        positions = sorted(positions_map.values(), key=lambda item: item["display_order"])
        for position in positions:
            total = sum(candidate["vote_count"] for candidate in position["candidates"])
            position["total_votes"] = total
            position["candidates"].sort(key=lambda item: item["vote_count"], reverse=True)

            for index, candidate in enumerate(position["candidates"], start=1):
                candidate["rank"] = index
                candidate["vote_percent"] = (
                    round((candidate["vote_count"] / total) * 100, 2) if total else 0.0
                )

            leader = position["candidates"][0] if position["candidates"] else None
            runner_up = position["candidates"][1] if len(position["candidates"]) > 1 else None
            margin_percent = 0.0
            margin_votes = 0
            if leader and runner_up:
                margin_votes = leader["vote_count"] - runner_up["vote_count"]
                margin_percent = round(leader["vote_percent"] - runner_up["vote_percent"], 2)

            position["leader"] = self._candidate_summary(leader) if leader else None
            position["runner_up"] = self._candidate_summary(runner_up) if runner_up else None
            position["margin_percent"] = margin_percent
            position["margin_votes"] = margin_votes
            position["chart"] = {
                "labels": [candidate["full_name"] for candidate in position["candidates"]],
                "vote_counts": [candidate["vote_count"] for candidate in position["candidates"]],
                "percentages": [candidate["vote_percent"] for candidate in position["candidates"]],
            }

        return positions

    def _build_highlights(self, positions: list[dict]) -> dict:
        all_candidates = []
        closest_races = []
        leading_by_position = []

        for position in positions:
            if position["leader"]:
                leading_by_position.append(
                    {
                        "position_uuid": position["position_uuid"],
                        "position_title": position["position_title"],
                        "leader": position["leader"],
                        "vote_percent": position["leader"]["vote_percent"],
                    }
                )
            if len(position["candidates"]) >= 2 and position["total_votes"] > 0:
                closest_races.append(
                    {
                        "position_uuid": position["position_uuid"],
                        "position_title": position["position_title"],
                        "leader": position["leader"],
                        "runner_up": position["runner_up"],
                        "margin_percent": position["margin_percent"],
                        "margin_votes": position["margin_votes"],
                        "total_votes": position["total_votes"],
                    }
                )
            for candidate in position["candidates"]:
                all_candidates.append(
                    {
                        **candidate,
                        "position_uuid": position["position_uuid"],
                        "position_title": position["position_title"],
                    }
                )

        closest_races.sort(key=lambda item: (item["margin_percent"], -item["total_votes"]))
        top_trending = sorted(all_candidates, key=lambda item: item["vote_count"], reverse=True)[:6]
        highest_turnout_position = max(
            positions,
            key=lambda item: item["total_votes"],
            default=None,
        )

        return {
            "top_trending": [self._candidate_card(candidate) for candidate in top_trending],
            "closest_races": closest_races[:5],
            "closest_race": closest_races[0] if closest_races else None,
            "leading_by_position": leading_by_position,
            "highest_turnout_position": (
                {
                    "position_uuid": highest_turnout_position["position_uuid"],
                    "position_title": highest_turnout_position["position_title"],
                    "total_votes": highest_turnout_position["total_votes"],
                }
                if highest_turnout_position and highest_turnout_position["total_votes"] > 0
                else None
            ),
        }

    @staticmethod
    def _candidate_summary(candidate: dict | None) -> dict | None:
        if not candidate:
            return None
        return {
            "candidate_uuid": candidate["candidate_uuid"],
            "full_name": candidate["full_name"],
            "vote_count": candidate["vote_count"],
            "vote_percent": candidate["vote_percent"],
            "image_path": candidate.get("image_path", ""),
            "rank": candidate.get("rank"),
        }

    @staticmethod
    def _candidate_card(candidate: dict) -> dict:
        return {
            "candidate_uuid": candidate["candidate_uuid"],
            "full_name": candidate["full_name"],
            "position_uuid": candidate["position_uuid"],
            "position_title": candidate["position_title"],
            "vote_count": candidate["vote_count"],
            "vote_percent": candidate["vote_percent"],
            "image_path": candidate.get("image_path", ""),
            "rank": candidate.get("rank"),
        }


election_live_trend_service = ElectionLiveTrendService()
