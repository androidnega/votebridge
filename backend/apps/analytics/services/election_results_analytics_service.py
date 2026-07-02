"""Completed-election analytics for admin reporting and inspection."""

from django.utils import timezone

from apps.analytics.repositories.election_analytics_repository import ElectionAnalyticsRepository
from apps.elections.models import Election
from apps.elections.repositories.election_repository import ElectionRepository
from apps.results.repositories.election_result_repository import ElectionResultRepository
from core.exceptions import NotFoundError, ValidationError

COMPLETED_ELECTION_STATUSES = {Election.Status.CLOSED, Election.Status.ARCHIVED}


class ElectionResultsAnalyticsService:
    def __init__(
        self,
        repository: ElectionAnalyticsRepository | None = None,
        election_repository: ElectionRepository | None = None,
        result_repository: ElectionResultRepository | None = None,
    ):
        self.repository = repository or ElectionAnalyticsRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.result_repository = result_repository or ElectionResultRepository()

    def get_results_analytics(self, election_uuid) -> dict:
        election = self._get_completed_election(election_uuid)
        aggregates = self.repository.aggregate_position_candidate_votes(election)
        positions = self._build_positions(aggregates)
        counts = self.repository.election_counts(election)
        result = self.result_repository.get_by_election(election)

        turnout_percent = 0.0
        if counts["eligible_voters"]:
            turnout_percent = round((counts["ballots_submitted"] / counts["eligible_voters"]) * 100, 2)

        highlights = self._build_highlights(positions)
        programme_breakdown = self.repository.programme_turnout_breakdown(election)
        channel_breakdown = self.repository.channel_breakdown(election)
        candidate_series = self.repository.candidate_hourly_series(election)

        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "election_status": election.status,
            "result_status": result.status if result else None,
            "last_updated": timezone.now().isoformat(),
            "summary": {
                "eligible_voters": counts["eligible_voters"],
                "ballots_submitted": counts["ballots_submitted"],
                "turnout_percent": float(result.turnout_percentage) if result else turnout_percent,
                "total_votes_cast": counts["total_votes_cast"],
                "positions_total": counts["positions"],
                "candidates_total": counts["candidates"],
                "closest_race": highlights["closest_race"],
                "biggest_win_margin": highlights["biggest_win_margin"],
                "most_competitive_position": highlights["most_competitive_position"],
            },
            "positions": positions,
            "candidates": highlights["candidate_performance"],
            "charts": {
                "votes_by_position": {
                    "labels": [position["position_title"] for position in positions],
                    "values": [position["total_votes"] for position in positions],
                },
                "hourly_votes": self.repository.vote_hourly_buckets(election, hours=168),
                "cumulative_ballots": self.repository.cumulative_ballot_timeline(election),
                "turnout_by_programme": programme_breakdown,
                "turnout_by_faculty": self._faculty_turnout(programme_breakdown),
                "channel_split": channel_breakdown,
                "candidate_hourly": candidate_series[:8],
            },
            "standings": result.standings if result and result.standings else None,
        }

    def _get_completed_election(self, election_uuid) -> Election:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")
        if election.status not in COMPLETED_ELECTION_STATUSES:
            raise ValidationError(
                message="Results analytics are available after an election is closed.",
                code="election_not_completed",
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

            max_votes = position["candidates"][0]["vote_count"] if position["candidates"] else 0
            winners = [
                candidate["candidate_uuid"]
                for candidate in position["candidates"]
                if candidate["vote_count"] == max_votes and max_votes > 0
            ]

            for index, candidate in enumerate(position["candidates"], start=1):
                candidate["rank"] = index
                candidate["vote_percent"] = (
                    round((candidate["vote_count"] / total) * 100, 2) if total else 0.0
                )
                candidate["is_winner"] = candidate["candidate_uuid"] in winners

            leader = position["candidates"][0] if position["candidates"] else None
            runner_up = position["candidates"][1] if len(position["candidates"]) > 1 else None
            margin_votes = 0
            margin_percent = 0.0
            if leader and runner_up:
                margin_votes = leader["vote_count"] - runner_up["vote_count"]
                margin_percent = round(leader["vote_percent"] - runner_up["vote_percent"], 2)

            position["winner"] = self._candidate_summary(leader) if leader and leader["is_winner"] else None
            position["runner_up"] = self._candidate_summary(runner_up) if runner_up else None
            position["margin_votes"] = margin_votes
            position["margin_percent"] = margin_percent
            position["chart"] = {
                "labels": [candidate["full_name"] for candidate in position["candidates"]],
                "vote_counts": [candidate["vote_count"] for candidate in position["candidates"]],
                "percentages": [candidate["vote_percent"] for candidate in position["candidates"]],
            }

        return positions

    def _build_highlights(self, positions: list[dict]) -> dict:
        closest_races = []
        biggest_win = None
        candidate_performance = []

        for position in positions:
            if len(position["candidates"]) >= 2 and position["total_votes"] > 0:
                race = {
                    "position_uuid": position["position_uuid"],
                    "position_title": position["position_title"],
                    "winner": position["winner"],
                    "runner_up": position["runner_up"],
                    "margin_percent": position["margin_percent"],
                    "margin_votes": position["margin_votes"],
                    "total_votes": position["total_votes"],
                }
                closest_races.append(race)
                if not biggest_win or race["margin_percent"] > biggest_win["margin_percent"]:
                    biggest_win = race

            for candidate in position["candidates"]:
                top_competitor = next(
                    (
                        other
                        for other in position["candidates"]
                        if other["candidate_uuid"] != candidate["candidate_uuid"]
                    ),
                    None,
                )
                candidate_performance.append(
                    {
                        **candidate,
                        "position_uuid": position["position_uuid"],
                        "position_title": position["position_title"],
                        "top_competitor": self._candidate_summary(top_competitor),
                        "margin_to_leader": (
                            position["winner"]["vote_count"] - candidate["vote_count"]
                            if position["winner"]
                            else 0
                        ),
                    }
                )

        closest_races.sort(key=lambda item: (item["margin_percent"], -item["total_votes"]))
        candidate_performance.sort(
            key=lambda item: (item["position_title"], item.get("rank", 99))
        )

        return {
            "closest_race": closest_races[0] if closest_races else None,
            "most_competitive_position": closest_races[0] if closest_races else None,
            "biggest_win_margin": biggest_win,
            "candidate_performance": candidate_performance,
        }

    @staticmethod
    def _candidate_summary(candidate: dict | None) -> dict | None:
        if not candidate:
            return None
        return {
            "candidate_uuid": candidate["candidate_uuid"],
            "full_name": candidate["full_name"],
            "vote_count": candidate["vote_count"],
            "vote_percent": candidate.get("vote_percent", 0.0),
            "image_path": candidate.get("image_path", ""),
            "rank": candidate.get("rank"),
            "is_winner": candidate.get("is_winner", False),
        }

    @staticmethod
    def _faculty_turnout(programme_rows: list[dict]) -> list[dict]:
        buckets: dict[str, dict] = {}
        for row in programme_rows:
            faculty = row["faculty"]
            bucket = buckets.setdefault(faculty, {"faculty": faculty, "eligible": 0, "participated": 0})
            bucket["eligible"] += row["eligible"]
            bucket["participated"] += row["participated"]

        results = []
        for faculty, data in sorted(buckets.items()):
            eligible = data["eligible"]
            participated = data["participated"]
            results.append(
                {
                    **data,
                    "turnout_percent": round((participated / eligible) * 100, 1) if eligible else 0.0,
                }
            )
        return results


election_results_analytics_service = ElectionResultsAnalyticsService()
