from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from datetime import timedelta

from apps.voting.validators import validate_election_is_open
from apps.security.models import SVTToken


def _check_svt_ownership_and_election(svt: SVTToken, user, election) -> None:
    if svt.user_id != user.id:
        raise DjangoValidationError("This voting token does not belong to you.")
    if svt.election_id != election.id:
        raise DjangoValidationError("This voting token does not belong to this election.")


def _check_svt_not_expired_or_revoked(svt: SVTToken) -> None:
    svt.mark_expired_if_needed()
    if svt.status == SVTToken.Status.EXPIRED:
        raise DjangoValidationError("This voting token has expired.")
    if svt.status == SVTToken.Status.REVOKED:
        raise DjangoValidationError("This voting token has been revoked.")
    if svt.is_expired:
        svt.status = SVTToken.Status.EXPIRED
        svt.save(update_fields=["status"])
        raise DjangoValidationError("This voting token has expired.")


def validate_svt_for_ballot_start(svt: SVTToken, user, election) -> None:
    """Ensure an SVT can begin a ballot session (issued only)."""
    _check_svt_ownership_and_election(svt, user, election)
    _check_svt_not_expired_or_revoked(svt)
    if svt.status == SVTToken.Status.USED:
        raise DjangoValidationError("This voting token has already been used.")
    if svt.status == SVTToken.Status.VALIDATED:
        raise DjangoValidationError("This voting token is already active for a ballot session.")
    if svt.status != SVTToken.Status.ISSUED:
        raise DjangoValidationError("This voting token is not valid.")


def validate_svt_for_ballot_submit(svt: SVTToken, user, election) -> None:
    """Ensure an SVT is ready for ballot submission (validated only)."""
    _check_svt_ownership_and_election(svt, user, election)
    _check_svt_not_expired_or_revoked(svt)
    if svt.status == SVTToken.Status.USED:
        raise DjangoValidationError("This voting token has already been used.")
    if svt.status != SVTToken.Status.VALIDATED:
        raise DjangoValidationError("Ballot session is not active. Validate your token first.")
    _check_ballot_session_active(svt)


def _check_ballot_session_active(svt: SVTToken) -> None:
    from django.conf import settings

    if not svt.validated_at:
        return
    session_minutes = int(getattr(settings, "BALLOT_SESSION_MINUTES", 15))
    deadline = svt.validated_at + timedelta(minutes=session_minutes)
    if timezone.now() >= deadline:
        svt.status = SVTToken.Status.EXPIRED
        svt.save(update_fields=["status"])
        raise DjangoValidationError("Your ballot session has expired. Request a new voting token.")


def validate_svt_for_voting(svt: SVTToken, user, election) -> None:
    """Backward-compatible alias for ballot submit validation."""
    validate_svt_for_ballot_submit(svt, user, election)


def validate_svt_for_verification(svt: SVTToken, user) -> None:
    """Ensure an SVT can be used to verify a ballot."""
    if svt.user_id != user.id:
        raise DjangoValidationError("This voting token does not belong to you.")
    if svt.status not in {SVTToken.Status.USED, SVTToken.Status.VALIDATED, SVTToken.Status.ISSUED}:
        if svt.status == SVTToken.Status.REVOKED:
            raise DjangoValidationError("This voting token has been revoked.")
        if svt.status == SVTToken.Status.EXPIRED:
            raise DjangoValidationError("This voting token has expired.")
        raise DjangoValidationError("This voting token cannot be used for verification.")


def validate_election_open_for_svt(election) -> None:
    validate_election_is_open(election)


def validate_svt_not_past_expiry(expires_at) -> None:
    if expires_at <= timezone.now():
        raise DjangoValidationError("Expiry time must be in the future.")
