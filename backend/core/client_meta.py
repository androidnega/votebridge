"""Extract client metadata from HTTP requests for monitoring."""

import hashlib
import ipaddress


def get_client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


def get_browser_fingerprint(request) -> str | None:
    raw = request.META.get("HTTP_X_DEVICE_FINGERPRINT", "").strip()
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_client_context(request) -> dict:
    return {
        "ip_address": get_client_ip(request),
        "user_agent": get_user_agent(request),
        "browser_fingerprint": get_browser_fingerprint(request),
    }
