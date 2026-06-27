from django.db.models import Q, QuerySet

from apps.elections.models import VoterEligibility


class VoterEligibilityRepository:
    def get_queryset(self) -> QuerySet[VoterEligibility]:
        return VoterEligibility.objects.select_related(
            "election",
            "user",
            "verified_by",
        ).all()

    def get_by_uuid(self, uuid) -> VoterEligibility | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def get_by_election_and_user(self, election, user) -> VoterEligibility | None:
        return self.get_queryset().filter(election=election, user=user).first()

    def list_for_election(
        self,
        election_uuid,
        is_eligible: bool | None = None,
    ) -> QuerySet[VoterEligibility]:
        queryset = self.get_queryset().filter(election__uuid=election_uuid)
        if is_eligible is not None:
            queryset = queryset.filter(is_eligible=is_eligible)
        return queryset

    def create(self, **data) -> VoterEligibility:
        return VoterEligibility.objects.create(**data)

    def update(self, eligibility: VoterEligibility, **data) -> VoterEligibility:
        for field, value in data.items():
            setattr(eligibility, field, value)
        eligibility.save()
        return eligibility

    def delete(self, eligibility: VoterEligibility) -> None:
        eligibility.delete()

    def search(
        self,
        election_uuid,
        query: str | None = None,
        is_eligible: bool | None = None,
    ) -> QuerySet[VoterEligibility]:
        queryset = self.list_for_election(election_uuid, is_eligible=is_eligible)
        if query:
            queryset = queryset.filter(
                Q(user__email__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__index_number__icontains=query)
                | Q(eligibility_reason__icontains=query)
            )
        return queryset

    def is_user_eligible(self, election, user) -> bool:
        record = self.get_by_election_and_user(election, user)
        if record is None:
            return False
        return record.is_eligible

    def get_eligible_positions_for_user(self, election, user):
        """Foundation for voting engine — returns active positions if voter is eligible."""
        if not self.is_user_eligible(election, user):
            return election.positions.none()
        return election.positions.filter(is_active=True)

    def get_eligible_voters_for_election(self, election, limit: int | None = None):
        """Return eligibility records for voters marked eligible in an election."""
        qs = self.get_queryset().filter(election=election, is_eligible=True).select_related("user")
        if limit:
            qs = qs[:limit]
        return qs
