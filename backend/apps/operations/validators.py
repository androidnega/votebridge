ACTIVITY_CATEGORIES = frozenset(
    {
        "users",
        "election",
        "security",
        "fraud",
        "strongroom",
        "ussd",
        "communications",
        "system",
    }
)

LOG_EXPORT_LIMIT = 5000


def validate_activity_category(category: str | None) -> str | None:
    if not category:
        return None
    normalized = category.strip().lower()
    if normalized not in ACTIVITY_CATEGORIES:
        from core.exceptions import ValidationError

        raise ValidationError(
            message=f"Invalid activity category: {category}",
            code="invalid_category",
        )
    return normalized
