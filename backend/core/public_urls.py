"""Helpers for building externally reachable VoteBridge URLs."""

from django.conf import settings

USSD_CALLBACK_PATH = "/api/v1/ussd/callback/"


def get_public_base_url() -> str:
    return (getattr(settings, "PUBLIC_BASE_URL", "") or "").rstrip("/")


def build_public_url(path: str) -> str:
    """Build an absolute public URL when PUBLIC_BASE_URL is configured."""
    normalized = path if path.startswith("/") else f"/{path}"
    base = get_public_base_url()
    if not base:
        return normalized
    return f"{base}{normalized}"
