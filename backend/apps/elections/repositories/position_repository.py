from django.db.models import Q, QuerySet

from apps.elections.models import Position


class PositionRepository:
    def get_queryset(self) -> QuerySet[Position]:
        return Position.objects.select_related("election").all()

    def get_by_uuid(self, uuid) -> Position | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def list_for_election(self, election_uuid) -> QuerySet[Position]:
        return self.get_queryset().filter(election__uuid=election_uuid)

    def create(self, **data) -> Position:
        return Position.objects.create(**data)

    def update(self, position: Position, **data) -> Position:
        for field, value in data.items():
            setattr(position, field, value)
        position.save()
        return position

    def delete(self, position: Position) -> None:
        position.delete()

    def search(
        self,
        election_uuid,
        query: str | None = None,
        is_active: bool | None = None,
    ) -> QuerySet[Position]:
        queryset = self.list_for_election(election_uuid)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def count_active_for_election(self, election) -> int:
        return Position.objects.filter(election=election, is_active=True).count()
