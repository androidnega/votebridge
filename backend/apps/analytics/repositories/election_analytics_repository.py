"""Read-only election analytics queries — live trends and completed-election charts."""

from collections import defaultdict
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncHour
from django.utils import timezone

from apps.analytics.repositories.analytics_repository import AnalyticsRepository
from apps.elections.models import Election, Position, VoterEligibility
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository


class ElectionAnalyticsRepository:
    def __init__(
        self,
        vote_repository: VoteRepository | None = None,
        analytics_repository: AnalyticsRepository | None = None,
    ):
        self.vote_repository = vote_repository or VoteRepository()
        self.analytics_repository = analytics_repository or AnalyticsRepository()

    def aggregate_position_candidate_votes(self, election: Election) -> list[dict]:
        return list(
            Vote.objects.filter(election=election)
            .values(
                "position__uuid",
                "position__title",
                "position__display_order",
                "position__max_votes_allowed",
                "candidate__uuid",
                "candidate__full_name",
                "candidate__department",
                "candidate__image",
            )
            .annotate(vote_count=Count("vote_id"))
            .order_by("position__display_order", "-vote_count")
        )

    def vote_hourly_buckets(self, election: Election, hours: int = 48) -> list[dict]:
        since = timezone.now() - timedelta(hours=hours)
        if election.end_date and election.end_date < timezone.now():
            since = max(since, election.start_date) if election.start_date else since

        rows = (
            Vote.objects.filter(election=election, timestamp__gte=since)
            .annotate(bucket=TruncHour("timestamp"))
            .values("bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        return [
            {"label": row["bucket"].strftime("%b %d %H:00"), "value": row["count"]}
            for row in rows
            if row["bucket"]
        ]

    def cumulative_ballot_timeline(self, election: Election) -> list[dict]:
        rows = (
            Vote.objects.filter(election=election)
            .annotate(bucket=TruncHour("timestamp"))
            .values("bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        cumulative = 0
        series = []
        for row in rows:
            if not row["bucket"]:
                continue
            cumulative += row["count"]
            series.append(
                {
                    "label": row["bucket"].strftime("%b %d %H:00"),
                    "value": cumulative,
                    "hourly": row["count"],
                }
            )
        return series

    def candidate_hourly_series(self, election: Election, hours: int = 48) -> list[dict]:
        since = timezone.now() - timedelta(hours=hours)
        rows = (
            Vote.objects.filter(election=election, timestamp__gte=since)
            .annotate(bucket=TruncHour("timestamp"))
            .values("candidate__uuid", "candidate__full_name", "bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        grouped: dict[str, dict] = {}
        for row in rows:
            candidate_uuid = str(row["candidate__uuid"])
            if candidate_uuid not in grouped:
                grouped[candidate_uuid] = {
                    "candidate_uuid": candidate_uuid,
                    "full_name": row["candidate__full_name"],
                    "points": [],
                }
            if row["bucket"]:
                grouped[candidate_uuid]["points"].append(
                    {
                        "label": row["bucket"].strftime("%b %d %H:00"),
                        "value": row["count"],
                    }
                )
        return list(grouped.values())

    def channel_breakdown(self, election: Election) -> list[dict]:
        rows = (
            Vote.objects.filter(election=election)
            .values("channel__channel_name")
            .annotate(count=Count("vote_id"))
            .order_by("-count")
        )
        return [
            {"channel": row["channel__channel_name"] or "unknown", "votes": row["count"]}
            for row in rows
        ]

    def programme_turnout_breakdown(self, election: Election) -> list[dict]:
        eligible_by_programme: dict[str, set] = defaultdict(set)
        voted_by_programme: dict[str, set] = defaultdict(set)

        for row in VoterEligibility.objects.filter(election=election, is_eligible=True).select_related(
            "user"
        ):
            code = self.analytics_repository.parse_programme_code(row.user.index_number) or "UNK"
            eligible_by_programme[code].add(row.user_id)

        for row in (
            Vote.objects.filter(election=election)
            .values("user_id", "user__index_number")
            .distinct()
        ):
            code = self.analytics_repository.parse_programme_code(row.get("user__index_number")) or "UNK"
            voted_by_programme[code].add(row["user_id"])

        results = []
        for code, eligible_ids in sorted(eligible_by_programme.items()):
            eligible = len(eligible_ids)
            participated = len(voted_by_programme.get(code, set()) & eligible_ids)
            results.append(
                {
                    "code": code,
                    "label": self.analytics_repository.programme_label(code),
                    "faculty": self.analytics_repository.faculty_for_programme(code),
                    "eligible": eligible,
                    "participated": participated,
                    "turnout_percent": round((participated / eligible) * 100, 1) if eligible else 0.0,
                }
            )
        return results

    def election_counts(self, election: Election) -> dict:
        positions = Position.objects.filter(election=election, is_active=True).count()
        from apps.candidates.models import Candidate

        candidates = Candidate.objects.filter(
            election=election,
            status=Candidate.Status.APPROVED,
        ).count()
        eligible = VoterEligibility.objects.filter(election=election, is_eligible=True).count()
        ballots = self.vote_repository.count_distinct_voters(election)
        votes = self.vote_repository.count_for_election(election)
        return {
            "positions": positions,
            "candidates": candidates,
            "eligible_voters": eligible,
            "ballots_submitted": ballots,
            "total_votes_cast": votes,
        }
