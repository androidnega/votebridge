"""Analytics-specific read helpers. Delegates domain queries to existing repositories."""

import re
from collections import defaultdict
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.elections.models import Election, VoterEligibility
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from apps.voting.models import Vote
from apps.voting.repositories.vote_repository import VoteRepository

PROGRAMME_LABELS = {
    "ITS": "Information Technology (Software)",
    "ITD": "Information Technology (Database)",
    "ITN": "Information Technology (Network)",
    "ICT": "Information and Communication Technology",
    "ACC": "Accounting",
    "MEE": "Mechanical Engineering",
}

FACULTY_BY_PROGRAMME = {
    "ITS": "Faculty of Applied Sciences",
    "ITD": "Faculty of Applied Sciences",
    "ITN": "Faculty of Applied Sciences",
    "ICT": "Faculty of Applied Sciences",
    "ACC": "Faculty of Business Studies",
    "MEE": "Faculty of Engineering",
}

INDEX_PATTERN = re.compile(r"^[A-Z]{2}/([A-Z]{3})/\d{2}/\d{3}$")


class AnalyticsRepository:
    """Read-only aggregations for ABI — no business rules."""

    def __init__(
        self,
        election_repository: ElectionRepository | None = None,
        eligibility_repository: VoterEligibilityRepository | None = None,
        vote_repository: VoteRepository | None = None,
    ):
        self.election_repository = election_repository or ElectionRepository()
        self.eligibility_repository = eligibility_repository or VoterEligibilityRepository()
        self.vote_repository = vote_repository or VoteRepository()

    def parse_programme_code(self, index_number: str | None) -> str | None:
        if not index_number:
            return None
        normalized = index_number.strip().upper()
        match = INDEX_PATTERN.match(normalized)
        if not match:
            return None
        return match.group(1)

    def programme_label(self, code: str | None) -> str:
        if not code:
            return "Unknown"
        return PROGRAMME_LABELS.get(code, code)

    def faculty_for_programme(self, code: str | None) -> str:
        if not code:
            return "Unknown"
        return FACULTY_BY_PROGRAMME.get(code, "Unassigned faculty")

    def total_students(self) -> int:
        return User.objects.filter(role__name=Role.Name.STUDENT, is_active=True).count()

    def completed_elections_count(self) -> int:
        return Election.objects.filter(
            status__in=[Election.Status.CLOSED, Election.Status.ARCHIVED]
        ).count()

    def vote_hourly_buckets(self, hours: int = 24) -> list[dict]:
        since = timezone.now() - timedelta(hours=hours)
        rows = (
            Vote.objects.filter(timestamp__gte=since)
            .annotate(bucket=TruncHour("timestamp"))
            .values("bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        return [{"label": row["bucket"].strftime("%H:00"), "value": row["count"]} for row in rows]

    def vote_daily_buckets(self, days: int = 30) -> list[dict]:
        since = timezone.now() - timedelta(days=days)
        rows = (
            Vote.objects.filter(timestamp__gte=since)
            .annotate(bucket=TruncDate("timestamp"))
            .values("bucket")
            .annotate(count=Count("vote_id"))
            .order_by("bucket")
        )
        return [{"label": row["bucket"].isoformat(), "value": row["count"]} for row in rows]

    def participation_breakdown(self) -> dict:
        eligible_by_programme: dict[str, set] = defaultdict(set)
        voted_by_programme: dict[str, set] = defaultdict(set)

        eligibilities = VoterEligibility.objects.filter(is_eligible=True).select_related("user")
        for row in eligibilities:
            code = self.parse_programme_code(row.user.index_number) or "UNK"
            eligible_by_programme[code].add(row.user_id)

        votes = Vote.objects.values("user_id", "user__index_number").distinct()
        for row in votes:
            code = self.parse_programme_code(row.get("user__index_number")) or "UNK"
            voted_by_programme[code].add(row["user_id"])

        programmes = []
        for code, eligible_ids in sorted(eligible_by_programme.items()):
            voted = len(voted_by_programme.get(code, set()))
            eligible = len(eligible_ids)
            programmes.append(
                {
                    "code": code,
                    "label": self.programme_label(code),
                    "faculty": self.faculty_for_programme(code),
                    "eligible": eligible,
                    "participated": voted,
                    "turnout_percent": round((voted / eligible) * 100, 1) if eligible else 0.0,
                }
            )

        faculties: dict[str, dict] = {}
        for item in programmes:
            faculty = item["faculty"]
            bucket = faculties.setdefault(
                faculty,
                {"faculty": faculty, "eligible": 0, "participated": 0},
            )
            bucket["eligible"] += item["eligible"]
            bucket["participated"] += item["participated"]

        faculty_rows = []
        for faculty, data in faculties.items():
            eligible = data["eligible"]
            participated = data["participated"]
            faculty_rows.append(
                {
                    **data,
                    "turnout_percent": round((participated / eligible) * 100, 1) if eligible else 0.0,
                }
            )

        return {
            "programmes": programmes,
            "faculties": faculty_rows,
            "departments": programmes,
        }

    def channel_breakdown(self, election=None) -> list[dict]:
        qs = Vote.objects.all()
        if election:
            qs = qs.filter(election=election)
        rows = qs.values("channel__name").annotate(count=Count("vote_id")).order_by("-count")
        return [{"channel": row["channel__name"] or "unknown", "votes": row["count"]} for row in rows]

    def election_comparison(self, limit: int = 10) -> list[dict]:
        elections = Election.objects.filter(
            status__in=[Election.Status.CLOSED, Election.Status.ARCHIVED, Election.Status.OPEN]
        ).order_by("-start_date")[:limit]
        rows = []
        for election in elections:
            snapshot = self._safe_election_row(election)
            if snapshot:
                rows.append(snapshot)
        return rows

    def _safe_election_row(self, election: Election) -> dict:
        eligible = VoterEligibility.objects.filter(election=election, is_eligible=True).count()
        participated = (
            Vote.objects.filter(election=election).values("user_id").distinct().count()
        )
        turnout = round((participated / eligible) * 100, 1) if eligible else 0.0
        row = {
            "election_uuid": str(election.uuid),
            "title": election.title,
            "status": election.status,
            "eligible_voters": eligible,
            "turnout_percent": turnout,
            "channels": {
                "web": election.allow_web_voting,
                "ussd": election.allow_ussd_voting,
            },
        }
        if election.status != Election.Status.OPEN:
            row["votes_cast"] = self.vote_repository.count_for_election(election)
            row["voters_participated"] = participated
        return row
