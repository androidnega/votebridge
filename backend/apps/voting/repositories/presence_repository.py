from django.db.models import QuerySet

from apps.voting.models import PreVotePresenceCapture


class PreVotePresenceRepository:
    def get_queryset(self) -> QuerySet[PreVotePresenceCapture]:
        return PreVotePresenceCapture.objects.select_related("user", "election")

    def get_for_svt(self, svt_id) -> PreVotePresenceCapture | None:
        return self.get_queryset().filter(svt_id=svt_id).first()

    def get_for_user_election_svt(self, user, election, svt_id) -> PreVotePresenceCapture | None:
        return (
            self.get_queryset()
            .filter(user=user, election=election, svt_id=svt_id)
            .first()
        )

    def create(self, **data) -> PreVotePresenceCapture:
        return PreVotePresenceCapture.objects.create(**data)
