from apps.results.models import ElectionResult


class ElectionResultRepository:
    def get_queryset(self):
        return ElectionResult.objects.select_related(
            "election",
            "generated_by",
            "certified_by",
            "published_by",
            "archived_by",
        ).all()

    def get_by_uuid(self, result_uuid) -> ElectionResult | None:
        return self.get_queryset().filter(uuid=result_uuid).first()

    def get_by_election(self, election) -> ElectionResult | None:
        return self.get_queryset().filter(election=election).first()

    def get_by_election_uuid(self, election_uuid) -> ElectionResult | None:
        return self.get_queryset().filter(election__uuid=election_uuid).first()

    def create(self, **data) -> ElectionResult:
        return ElectionResult.objects.create(**data)

    def update(self, result: ElectionResult, **fields) -> ElectionResult:
        for key, value in fields.items():
            setattr(result, key, value)
        result.save()
        return result

    def list_filtered(self, status: str | None = None, published_only: bool = False):
        qs = self.get_queryset()
        if status:
            qs = qs.filter(status=status)
        if published_only:
            qs = qs.filter(status=ElectionResult.Status.PUBLISHED)
        return qs

    def list_certification_queue(self):
        return self.get_queryset().filter(
            status__in=[
                ElectionResult.Status.PENDING_CERTIFICATION,
                ElectionResult.Status.GENERATED,
            ]
        )

    def list_publication_queue(self):
        return self.get_queryset().filter(status=ElectionResult.Status.CERTIFIED)

    def list_archivable(self):
        return self.get_queryset().filter(status=ElectionResult.Status.PUBLISHED)
