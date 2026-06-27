from apps.fraud.models import FraudCase, SecurityAlert

RISK_WEIGHTS = {
    SecurityAlert.AlertType.DUPLICATE_DEVICE: 25,
    SecurityAlert.AlertType.DUPLICATE_LOCATION: 20,
    SecurityAlert.AlertType.MULTIPLE_ACCOUNTS_SAME_DEVICE: 40,
    SecurityAlert.AlertType.EXCESSIVE_LOGIN_ATTEMPTS: 15,
    SecurityAlert.AlertType.EXCESSIVE_SVT_REQUESTS: 15,
    SecurityAlert.AlertType.SUSPICIOUS_VOTING_PATTERN: 30,
}


def calculate_risk_score(alert_types: list[str]) -> int:
    """Sum risk weights for one or more alert types (capped at 100)."""
    total = sum(RISK_WEIGHTS.get(alert_type, 0) for alert_type in alert_types)
    return min(total, 100)


def calculate_risk_score_for_alert(alert_type: str) -> int:
    return calculate_risk_score([alert_type])


def severity_from_score(score: int) -> str:
    if score >= 80:
        return FraudCase.Severity.CRITICAL
    if score >= 60:
        return FraudCase.Severity.HIGH
    if score >= 30:
        return FraudCase.Severity.MEDIUM
    return FraudCase.Severity.LOW
