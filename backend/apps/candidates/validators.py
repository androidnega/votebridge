from django.core.exceptions import ValidationError as DjangoValidationError

from apps.candidates.models import Candidate
from apps.elections.models import Election, Position
from apps.elections.position_validators import validate_position_belongs_to_election


def validate_candidate_election_editable(election: Election):
    if election.is_read_only:
        raise DjangoValidationError(
            "Candidates cannot be modified for closed or archived elections."
        )


def validate_unique_candidate_name(election: Election, full_name: str, exclude_uuid=None):
    queryset = Candidate.objects.filter(election=election, full_name=full_name)
    if exclude_uuid:
        queryset = queryset.exclude(uuid=exclude_uuid)
    if queryset.exists():
        raise DjangoValidationError(
            "Candidate name must be unique within the election."
        )


def validate_unique_candidate_user(election: Election, user, exclude_uuid=None):
    if user is None:
        return
    queryset = Candidate.objects.filter(election=election, user=user)
    if exclude_uuid:
        queryset = queryset.exclude(uuid=exclude_uuid)
    if queryset.exists():
        raise DjangoValidationError(
            "This student is already registered as a candidate in this election."
        )


def validate_candidate_position(position: Position, election: Election):
    if position is None:
        raise DjangoValidationError("Every candidate must belong to a position.")
    validate_position_belongs_to_election(position, election)
    if not position.is_active:
        raise DjangoValidationError(
            "Candidate cannot be assigned to an inactive position."
        )
