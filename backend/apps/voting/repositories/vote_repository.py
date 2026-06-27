from django.db.models import Count, QuerySet

from apps.voting.models import Vote


class VoteRepository:
    def get_queryset(self) -> QuerySet[Vote]:
        return Vote.objects.select_related(
            "election",
            "position",
            "candidate",
            "user",
            "channel",
        ).all()

    def get_by_vote_id(self, vote_id) -> Vote | None:
        return self.get_queryset().filter(vote_id=vote_id).first()

    def get_by_svt_id(self, svt_id) -> Vote | None:
        return self.get_queryset().filter(svt_id=svt_id).first()

    def list_by_svt_id(self, svt_id):
        return self.get_queryset().filter(svt_id=svt_id).order_by("timestamp")

    def get_by_vote_hash(self, vote_hash: str) -> Vote | None:
        return self.get_queryset().filter(vote_hash=vote_hash).first()

    def create(self, **data) -> Vote:
        return Vote.objects.create(**data)

    def list_for_user_in_election(self, user, election):
        return self.get_queryset().filter(user=user, election=election)

    def list_for_user_position(self, user, position):
        return self.get_queryset().filter(user=user, position=position)

    def count_for_user_position(self, user, position) -> int:
        return Vote.objects.filter(user=user, position=position).count()

    def has_vote_for_user_position_candidate(self, user, position, candidate) -> bool:
        return Vote.objects.filter(
            user=user,
            position=position,
            candidate=candidate,
        ).exists()

    def user_has_voted_position(self, user, position) -> bool:
        return Vote.objects.filter(user=user, position=position).exists()

    def list_for_election(self, election):
        return self.get_queryset().filter(election=election).order_by("timestamp")

    def count_for_election(self, election) -> int:
        return Vote.objects.filter(election=election).count()

    def count_distinct_voters(self, election) -> int:
        return (
            Vote.objects.filter(election=election)
            .values("user_id")
            .distinct()
            .count()
        )

    def aggregate_votes_by_position_candidate(self, election) -> list[dict]:
        return list(
            Vote.objects.filter(election=election)
            .values(
                "position_id",
                "position__uuid",
                "position__title",
                "position__max_votes_allowed",
                "position__display_order",
                "candidate_id",
                "candidate__uuid",
                "candidate__full_name",
                "candidate__department",
            )
            .annotate(vote_count=Count("vote_id"))
            .order_by("position__display_order", "-vote_count")
        )

    def verify_hashes_for_election(self, election) -> dict:
        invalid = []
        for vote in self.list_for_election(election).iterator():
            expected = Vote.compute_vote_hash(
                election_id=vote.election_id,
                position_id=vote.position_id,
                candidate_id=vote.candidate_id,
                user_id=vote.user_id,
                channel_id=vote.channel_id,
                timestamp_iso=vote.timestamp.isoformat(),
            )
            if vote.vote_hash != expected:
                invalid.append(str(vote.vote_id))
        return {"passed": len(invalid) == 0, "invalid_count": len(invalid), "invalid_vote_ids": invalid[:50]}

    def check_max_votes_per_position(self, election) -> dict:
        violations = []
        from apps.elections.models import Position

        for position in Position.objects.filter(election=election, is_active=True):
            user_counts = (
                Vote.objects.filter(election=election, position=position)
                .values("user_id")
                .annotate(vote_count=Count("vote_id"))
            )
            for row in user_counts:
                if row["vote_count"] > position.max_votes_allowed:
                    violations.append(
                        {
                            "position_uuid": str(position.uuid),
                            "user_id": row["user_id"],
                            "vote_count": row["vote_count"],
                            "max_allowed": position.max_votes_allowed,
                        }
                    )
        return {"passed": len(violations) == 0, "violations": violations[:50]}
