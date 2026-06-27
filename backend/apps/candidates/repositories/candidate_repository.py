from django.db.models import QuerySet

from apps.candidates.models import Candidate


class CandidateRepository:
    def get_queryset(self) -> QuerySet[Candidate]:
        return Candidate.objects.select_related("election", "position").all()

    def get_by_uuid(self, uuid) -> Candidate | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def list_for_election(self, election_uuid) -> QuerySet[Candidate]:
        return self.get_queryset().filter(election__uuid=election_uuid)

    def create(self, **data) -> Candidate:
        return Candidate.objects.create(**data)

    def update(self, candidate: Candidate, **data) -> Candidate:
        for field, value in data.items():
            setattr(candidate, field, value)
        candidate.save()
        return candidate

    def delete(self, candidate: Candidate) -> None:
        candidate.delete()

    def count_approved_for_election(self, election) -> int:
        return Candidate.objects.filter(
            election=election,
            status=Candidate.Status.APPROVED,
        ).count()
