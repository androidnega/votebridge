from django.core.exceptions import ValidationError as DjangoValidationError

from apps.elections.models import Election, Position


def validate_position_belongs_to_election(position: Position, election: Election):
    if position.election_id != election.id:
        raise DjangoValidationError(
            "Position does not belong to this election."
        )


def validate_max_votes_allowed(value: int):
    if value < 1:
        raise DjangoValidationError("max_votes_allowed must be at least 1.")


def validate_position_election_editable(election: Election):
    if election.is_read_only:
        raise DjangoValidationError(
            "Positions cannot be modified for closed or archived elections."
        )


def validate_unique_position_title(election: Election, title: str, exclude_uuid=None):
    queryset = Position.objects.filter(election=election, title=title)
    if exclude_uuid:
        queryset = queryset.exclude(uuid=exclude_uuid)
    if queryset.exists():
        raise DjangoValidationError(
            "A position with this title already exists in this election."
        )
