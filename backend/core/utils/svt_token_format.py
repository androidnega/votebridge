"""Phase 59 — human-friendly Secure Voting Token format (VB-XXXX-XXXX)."""

from __future__ import annotations

import re
import secrets

SVT_PREFIX = "VB"
SVT_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
SVT_PATTERN = re.compile(r"^VB-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}$")


def generate_formatted_svt() -> str:
    segments = [
        "".join(secrets.choice(SVT_ALPHABET) for _ in range(4))
        for _ in range(2)
    ]
    return f"{SVT_PREFIX}-{segments[0]}-{segments[1]}"


def normalize_svt_token(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"[^A-Za-z0-9]", "", str(value).upper())
    if cleaned.startswith("SVT"):
        body = cleaned[3:]
    elif cleaned.startswith("VB"):
        body = cleaned[2:]
    else:
        body = cleaned
    if len(body) != 8 or not body.isalnum():
        return None
    return f"{SVT_PREFIX}-{body[:4]}-{body[4:8]}"


def is_valid_svt_format(value: str | None) -> bool:
    normalized = normalize_svt_token(value)
    return bool(normalized and SVT_PATTERN.match(normalized))


def format_partial_svt_input(value: str | None) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", str(value).upper())
    if cleaned.startswith("SVT"):
        body = cleaned[3:]
    elif cleaned.startswith("VB"):
        body = cleaned[2:]
    else:
        body = cleaned
    body = body[:8]
    if not body:
        return ""
    result = SVT_PREFIX
    if body:
        result += f"-{body[:4]}"
    if len(body) > 4:
        result += f"-{body[4:8]}"
    return result
