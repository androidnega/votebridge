from django.core.exceptions import ValidationError as DjangoValidationError

from apps.fraud.models import FraudCase, SecurityAlert


def validate_alert_status_transition(current_status: str, new_status: str) -> None:
    allowed = {
        SecurityAlert.Status.OPEN: {
            SecurityAlert.Status.REVIEWING,
            SecurityAlert.Status.RESOLVED,
            SecurityAlert.Status.ESCALATED,
        },
        SecurityAlert.Status.REVIEWING: {
            SecurityAlert.Status.RESOLVED,
            SecurityAlert.Status.ESCALATED,
        },
        SecurityAlert.Status.ESCALATED: {
            SecurityAlert.Status.REVIEWING,
            SecurityAlert.Status.RESOLVED,
        },
        SecurityAlert.Status.RESOLVED: set(),
    }
    if new_status not in allowed.get(current_status, set()):
        raise DjangoValidationError(
            f"Cannot transition alert from '{current_status}' to '{new_status}'."
        )


def validate_fraud_case_status_transition(current_status: str, new_status: str) -> None:
    allowed = {
        FraudCase.Status.OPEN: {
            FraudCase.Status.INVESTIGATING,
            FraudCase.Status.RESOLVED,
            FraudCase.Status.DISMISSED,
            FraudCase.Status.ESCALATED,
        },
        FraudCase.Status.INVESTIGATING: {
            FraudCase.Status.RESOLVED,
            FraudCase.Status.DISMISSED,
            FraudCase.Status.ESCALATED,
        },
        FraudCase.Status.ESCALATED: {
            FraudCase.Status.INVESTIGATING,
            FraudCase.Status.RESOLVED,
            FraudCase.Status.DISMISSED,
        },
        FraudCase.Status.RESOLVED: set(),
        FraudCase.Status.DISMISSED: set(),
    }
    if new_status not in allowed.get(current_status, set()):
        raise DjangoValidationError(
            f"Cannot transition fraud case from '{current_status}' to '{new_status}'."
        )


def validate_investigation_note(note: str) -> None:
    if not note or not note.strip():
        raise DjangoValidationError("Investigation note cannot be empty.")
    if len(note) > 5000:
        raise DjangoValidationError("Investigation note is too long.")
