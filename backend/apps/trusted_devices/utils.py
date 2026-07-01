import hashlib
import re
from dataclasses import dataclass

from django.conf import settings

from apps.security.models import parse_operating_system
from apps.trusted_devices.constants import TRUSTED_DEVICE_COOKIE


@dataclass
class DeviceContext:
    browser_fingerprint: str
    operating_system: str = ""
    browser_name: str = ""
    browser_version: str = ""
    platform: str = ""
    timezone: str = ""
    language: str = ""
    screen_resolution: str = ""
    device_name: str = ""

    def fingerprint_signature(self) -> str:
        parts = [
            self.browser_fingerprint,
            self.operating_system,
            self.browser_name,
            self.platform,
            self.timezone,
            self.language,
            self.screen_resolution,
        ]
        raw = "|".join(p for p in parts if p)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_browser_fingerprint(raw: str | None) -> str:
    """Return a stable fingerprint that fits security DeviceLog limits (128 chars)."""
    value = (raw or "").strip()
    if not value:
        return ""
    if len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower()):
        return value.lower()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_device_token(raw_token: str, user_uuid: str) -> str:
    payload = f"{raw_token}:{user_uuid}:{settings.SECRET_KEY}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_device_token() -> str:
    import secrets

    from apps.trusted_devices.constants import DEVICE_TOKEN_BYTES

    return secrets.token_urlsafe(DEVICE_TOKEN_BYTES)


def parse_browser(user_agent: str) -> tuple[str, str]:
    ua = user_agent or ""
    if "Edg/" in ua:
        match = re.search(r"Edg/([\d.]+)", ua)
        return "Edge", match.group(1) if match else ""
    if "Chrome/" in ua and "Chromium" not in ua:
        match = re.search(r"Chrome/([\d.]+)", ua)
        return "Chrome", match.group(1) if match else ""
    if "Firefox/" in ua:
        match = re.search(r"Firefox/([\d.]+)", ua)
        return "Firefox", match.group(1) if match else ""
    if "Safari/" in ua and "Chrome" not in ua:
        match = re.search(r"Version/([\d.]+)", ua)
        return "Safari", match.group(1) if match else ""
    return "Unknown", ""


def build_device_context(
    *,
    user_agent: str = "",
    browser_fingerprint: str = "",
    signals: dict | None = None,
) -> DeviceContext:
    signals = signals or {}
    os_name = signals.get("operating_system") or parse_operating_system(user_agent)
    browser_name, browser_version = parse_browser(user_agent)
    if signals.get("browser_name"):
        browser_name = signals["browser_name"]
    if signals.get("browser_version"):
        browser_version = signals["browser_version"]

    fp = normalize_browser_fingerprint(
        browser_fingerprint or signals.get("browser_fingerprint") or ""
    )
    if not fp and user_agent:
        fp = hashlib.sha256(user_agent.encode("utf-8")).hexdigest()

    return DeviceContext(
        browser_fingerprint=fp,
        operating_system=os_name,
        browser_name=browser_name,
        browser_version=browser_version,
        platform=signals.get("platform", ""),
        timezone=signals.get("timezone", ""),
        language=signals.get("language", ""),
        screen_resolution=signals.get("screen_resolution", ""),
        device_name=signals.get("device_name", ""),
    )


def fingerprint_match_score(stored_fp: str, current: DeviceContext) -> float:
    """Return 0–100 similarity; 100 = exact composite match."""
    if not stored_fp:
        return 0.0
    if stored_fp == current.browser_fingerprint:
        return 100.0
    if stored_fp == current.fingerprint_signature():
        return 95.0
    # Partial match on primary fingerprint component
    if current.browser_fingerprint and stored_fp.startswith(current.browser_fingerprint[:16]):
        return 60.0
    return 0.0


def default_device_name(context: DeviceContext) -> str:
    parts = [p for p in (context.browser_name, context.operating_system, context.platform) if p]
    return " — ".join(parts[:2]) if parts else "Trusted Device"


def set_trusted_device_cookie(response, raw_token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        TRUSTED_DEVICE_COOKIE,
        raw_token,
        max_age=max_age_seconds,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Strict",
        path="/",
    )


def clear_trusted_device_cookie(response) -> None:
    response.delete_cookie(TRUSTED_DEVICE_COOKIE, path="/")
