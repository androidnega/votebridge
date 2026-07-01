from django.db.models import QuerySet
from django.utils import timezone

from apps.security.models import SVTToken


class SVTRepository:
    def get_queryset(self) -> QuerySet[SVTToken]:
        return SVTToken.objects.select_related("user", "election").all()

    def get_by_svt_id(self, svt_id) -> SVTToken | None:
        return self.get_queryset().filter(svt_id=svt_id).first()

    def get_by_token_code(self, token_code: str) -> SVTToken | None:
        normalized = str(token_code or "").strip()
        if normalized.isdigit():
            normalized = normalized.zfill(6)
        token_hash = SVTToken.hash_token_code(normalized)
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

    def get_active_svt_for_user_election(self, user, election) -> SVTToken | None:
        """Return an issued (non-expired) or validated SVT that blocks re-issue."""
        candidates = self.get_queryset().filter(
            user=user,
            election=election,
            status__in=[SVTToken.Status.ISSUED, SVTToken.Status.VALIDATED],
        ).order_by("-issued_at")

        for svt in candidates:
            svt.mark_expired_if_needed()
            if svt.status == SVTToken.Status.VALIDATED:
                return svt
            if svt.status == SVTToken.Status.ISSUED and not svt.is_expired:
                return svt
        return None

    def has_active_svt_for_user_election(self, user, election) -> bool:
        return self.get_active_svt_for_user_election(user, election) is not None

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
