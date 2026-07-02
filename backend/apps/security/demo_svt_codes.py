"""Development-only shared Secure Voting Token codes for student demos."""

from __future__ import annotations

import re

from django.conf import settings

DEMO_SVT_PATTERN = re.compile(r"^VB-DEMO-(\d{4})$", re.I)
LEGACY_NUMERIC_DEMO_PATTERN = re.compile(r"^\d{6}$")

DEFAULT_DEMO_SVT_CODES: tuple[str, ...] = tuple(
    f"VB-DEMO-{index:04d}" for index in range(1, 11)
)

DEMO_SVT_FAR_FUTURE_YEAR = 2099


def normalize_demo_svt_code(value: str | None) -> str | None:
    """Normalize a demo SVT entry (VB-DEMO-0001 … or legacy 6-digit numeric)."""
    if not value:
        return None
    stripped = str(value).strip().upper()
    match = DEMO_SVT_PATTERN.match(stripped)
    if match:
        return f"VB-DEMO-{match.group(1)}"
    if LEGACY_NUMERIC_DEMO_PATTERN.match(stripped):
        return stripped
    return None


def is_demo_svt_code(value: str | None) -> bool:
    return normalize_demo_svt_code(value) is not None


def get_dev_demo_svt_codes() -> list[str]:
    """Return the active demo SVT pool (defaults + optional env overrides)."""
    configured = getattr(settings, "DEV_DEMO_SVT_CODES", None) or []
    codes: list[str] = []
    seen: set[str] = set()

    for raw in (*DEFAULT_DEMO_SVT_CODES, *configured):
        normalized = normalize_demo_svt_code(raw)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        codes.append(normalized)

    legacy = str(getattr(settings, "DEV_SVT_FALLBACK_CODE", "") or "").strip()
    legacy_normalized = normalize_demo_svt_code(legacy)
    if legacy_normalized and legacy_normalized not in seen:
        codes.append(legacy_normalized)

    return codes


def match_dev_demo_svt_code(value: str | None) -> str | None:
    """Return the normalized demo code when *value* is in the active pool."""
    normalized = normalize_demo_svt_code(value)
    if not normalized:
        return None
    if normalized in get_dev_demo_svt_codes():
        return normalized
    return None


def demo_svt_enabled() -> bool:
    if not getattr(settings, "DEV_SVT_FALLBACK_ENABLED", False):
        return False
    if settings.DEBUG is not True:
        return False
    return bool(get_dev_demo_svt_codes())
