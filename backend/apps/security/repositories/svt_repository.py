from django.db.models import QuerySet
from django.utils import timezone

from apps.security.models import SVTToken


class SVTRepository:
    def get_queryset(self) -> QuerySet[SVTToken]:
        return SVTToken.objects.select_related("user", "election").all()

    def get_by_svt_id(self, svt_id) -> SVTToken | None:
        return self.get_queryset().filter(svt_id=svt_id).first()

    def get_by_token_code(self, token_code: str) -> SVTToken | None:
        token_hash = SVTToken.hash_token_code(token_code)
        return self.get_queryset().filter(token_code=token_hash).first()

    def list_for_election(self, election, status: str | None = None):
        qs = self.get_queryset().filter(election=election)
        if status:
            qs = qs.filter(status=status)
        return qs

    def list_active_issued_for_user_election(self, user, election):
        return self.get_queryset().filter(
            user=user,
            election=election,
            status=SVTToken.Status.ISSUED,
            expires_at__gt=timezone.now(),
        )

    def create(self, **data) -> SVTToken:
        return SVTToken.objects.create(**data)

    def revoke_issued_for_user_election(self, user, election) -> int:
        return SVTToken.objects.filter(
            user=user,
            election=election,
            status__in=[SVTToken.Status.ISSUED, SVTToken.Status.VALIDATED],
        ).update(status=SVTToken.Status.REVOKED)

    def update(self, svt: SVTToken, **fields) -> SVTToken:
        for key, value in fields.items():
            setattr(svt, key, value)
        svt.save()
        return svt
