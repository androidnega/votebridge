from apps.system.constants import SETTING_CATEGORIES
from core.exceptions import ValidationError


def validate_category(category: str | None) -> str:
    if not category:
        raise ValidationError(message="Category is required.", code="missing_category")
    normalized = category.strip().lower()
    if normalized not in SETTING_CATEGORIES:
        raise ValidationError(message=f"Invalid category: {category}", code="invalid_category")
    return normalized


def validate_setting_key(key: str | None) -> str:
    if not key or not key.strip():
        raise ValidationError(message="Setting key is required.", code="missing_key")
    return key.strip()


def validate_step_up_token(token: str | None) -> str:
    if not token or not str(token).strip():
        raise ValidationError(
            message="Step-up authentication is required for this action.",
            code="step_up_required",
        )
    return str(token).strip()
