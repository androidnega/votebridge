from django.core.exceptions import ValidationError as DjangoValidationError

from apps.elections.models import Election


def validate_eligibility_election_editable(election: Election):
    if election.is_read_only:
        raise DjangoValidationError(
            "Voter eligibility cannot be modified for closed or archived elections."
        )


def validate_eligibility_unique(election: Election, user_id: int, exclude_uuid=None):
    from apps.elections.models import VoterEligibility

    queryset = VoterEligibility.objects.filter(election=election, user_id=user_id)
    if exclude_uuid:
        queryset = queryset.exclude(uuid=exclude_uuid)
    if queryset.exists():
        raise DjangoValidationError(
            "This voter already has an eligibility record for this election."
        )
