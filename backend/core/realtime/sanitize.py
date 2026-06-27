"""Strip result-sensitive fields while elections remain open."""

from apps.elections.models import Election

FORBIDDEN_KEYS = frozenset(
    {
        "candidate_name",
        "candidate_uuid",
        "candidate_id",
        "candidate_standings",
        "vote_totals",
        "vote_totals_by_candidate",
        "running_winner",
        "running_winners",
        "standings",
        "results",
        "winner",
        "winners",
    }
)


def sanitize_payload(payload: dict, election_status: str | None = None) -> dict:
    """Remove candidate-level or result data when the election is still open."""
    if not payload:
        return payload

    status = election_status or payload.get("election_status")
    if status != Election.Status.OPEN:
        return payload

    return _strip_forbidden(payload)


def _strip_forbidden(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                continue
            cleaned[key] = _strip_forbidden(item)
        return cleaned
    if isinstance(value, list):
        return [_strip_forbidden(item) for item in value]
    return value
