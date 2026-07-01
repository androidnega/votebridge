import re


def mask_phone_number(phone: str = "") -> str:
    """Mask a phone number for display, e.g. 024*****91."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < 4:
        return "**********"
    if digits.startswith("233") and len(digits) >= 12:
        local = f"0{digits[3:]}"
    else:
        local = digits if digits.startswith("0") else f"0{digits[-9:]}"
    if len(local) < 4:
        return "**********"
    return f"{local[:3]}{'*' * max(3, len(local) - 5)}{local[-2:]}"
