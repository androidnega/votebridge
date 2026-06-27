from core.exceptions import ValidationError

VALID_PERIODS = frozenset({"daily", "weekly", "monthly", "semester", "academic_year"})
VALID_REPORT_TYPES = frozenset(
    {
        "election",
        "participation",
        "security",
        "fraud",
        "operations",
        "communication",
        "strongroom",
        "institution",
    }
)
VALID_EXPORT_FORMATS = frozenset({"json", "csv", "excel", "pdf"})


def validate_period(period: str | None) -> str:
    normalized = (period or "daily").strip().lower()
    if normalized not in VALID_PERIODS:
        raise ValidationError(message=f"Invalid period: {period}", code="invalid_period")
    return normalized


def validate_report_type(report_type: str | None) -> str:
    if not report_type:
        raise ValidationError(message="Report type is required.", code="missing_report_type")
    normalized = report_type.strip().lower()
    if normalized not in VALID_REPORT_TYPES:
        raise ValidationError(message=f"Invalid report type: {report_type}", code="invalid_report_type")
    return normalized


def validate_export_format(fmt: str | None) -> str:
    normalized = (fmt or "json").strip().lower()
    if normalized not in VALID_EXPORT_FORMATS:
        raise ValidationError(message=f"Invalid export format: {fmt}", code="invalid_format")
    return normalized
