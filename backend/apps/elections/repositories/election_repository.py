from django.db.models import Q, QuerySet

from apps.elections.models import Election, VotingChannel


class ElectionRepository:
    def get_queryset(self) -> QuerySet[Election]:
        return Election.objects.select_related("created_by").all()

    def get_by_uuid(self, uuid) -> Election | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def create(self, **data) -> Election:
        return Election.objects.create(**data)

    def update(self, election: Election, **data) -> Election:
        for field, value in data.items():
            setattr(election, field, value)
        election.save()
        return election

    def delete(self, election: Election) -> None:
        election.delete()

    def search(
        self,
        query: str | None = None,
        status: str | None = None,
        election_type: str | None = None,
    ) -> QuerySet[Election]:
        queryset = self.get_queryset()
        if status:
            queryset = queryset.filter(status=status)
        if election_type:
            queryset = queryset.filter(election_type=election_type)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def count_approved_candidates(self, election: Election) -> int:
        return election.candidates.filter(status="approved").count()


class VotingChannelRepository:
    def get_queryset(self) -> QuerySet[VotingChannel]:
        return VotingChannel.objects.all()

    def get_by_uuid(self, uuid) -> VotingChannel | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def get_by_name(self, name: str) -> VotingChannel | None:
        return self.get_queryset().filter(channel_name=name).first()

    def create(self, **data) -> VotingChannel:
        return VotingChannel.objects.create(**data)

    def update(self, channel: VotingChannel, **data) -> VotingChannel:
        for field, value in data.items():
            setattr(channel, field, value)
        channel.save()
        return channel

    def delete(self, channel: VotingChannel) -> None:
        channel.delete()

    def list_active(self) -> QuerySet[VotingChannel]:
        return self.get_queryset().filter(is_active=True)
