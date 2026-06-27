from django.core.exceptions import ValidationError as DjangoValidationError

from apps.results.models import ElectionResult


def validate_result_status_transition(current: str, new_status: str) -> None:
    allowed = ElectionResult.STATUS_TRANSITIONS.get(current, set())
    if new_status not in allowed:
        raise DjangoValidationError(
            f"Cannot transition result from '{current}' to '{new_status}'."
        )


def validate_election_closed_for_results(election_status: str) -> None:
    from apps.elections.models import Election

    if election_status not in {Election.Status.CLOSED, Election.Status.ARCHIVED}:
        raise DjangoValidationError(
            "Results can only be generated after the election is closed."
        )
