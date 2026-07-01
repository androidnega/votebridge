"""Phone normalization helpers for OTP and USSD."""

import re


def normalize_phone(value: str) -> str:
    """Normalize to digits-only Ghana-friendly MSISDN (233XXXXXXXXX)."""
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""

    if digits.startswith("233") and len(digits) >= 12:
        return digits

    if digits.startswith("0") and len(digits) >= 10:
        return f"233{digits[1:]}"

    if len(digits) == 9:
        return f"233{digits}"

    return digits


def phones_match(a: str, b: str) -> bool:
    left = normalize_phone(a)
    right = normalize_phone(b)
    if not left or not right:
        return False
    if left == right:
        return True
    return left[-9:] == right[-9:]
