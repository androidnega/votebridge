from django.core.exceptions import ValidationError as DjangoValidationError

from apps.elections.models import Election


def validate_election_dates(start_date, end_date):
    if start_date and end_date and start_date >= end_date:
        raise DjangoValidationError("Election start date must be before end date.")


def validate_election_can_be_opened(election: Election):
    if not election.positions.filter(is_active=True).exists():
        raise DjangoValidationError(
            "Election cannot be opened without at least one active position."
        )
    if not election.candidates.filter(status="approved").exists():
        raise DjangoValidationError(
            "Election cannot be opened without approved candidates."
        )
    active_positions = election.positions.filter(is_active=True)
    for position in active_positions:
        if not position.candidates.filter(status="approved").exists():
            raise DjangoValidationError(
                f"Position '{position.title}' has no approved candidates."
            )


def validate_election_can_be_deleted(election: Election):
    if election.voting_has_begun:
        raise DjangoValidationError(
            "Election cannot be deleted after voting has begun."
        )


def validate_election_is_editable(election: Election):
    if election.is_read_only:
        raise DjangoValidationError("Closed or archived elections are read-only.")


def validate_status_transition(current_status: str, new_status: str):
    allowed = Election.STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise DjangoValidationError(
            f"Cannot transition election from '{current_status}' to '{new_status}'."
        )
