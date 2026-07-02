"""Development-only credential helpers — values must come from environment (.env)."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def require_dev_bootstrap_password() -> str:
    """Return the local bootstrap password configured for development seeds."""
    if not settings.DEBUG:
        raise ImproperlyConfigured("DEV_BOOTSTRAP_PASSWORD is only available when DEBUG=True.")

    password = str(getattr(settings, "DEV_BOOTSTRAP_PASSWORD", "") or "").strip()
    if not password:
        raise ImproperlyConfigured(
            "DEV_BOOTSTRAP_PASSWORD is not set. Add it to your local .env file "
            "(see .env.example)."
        )
    return password


def dev_otp_fallback_code() -> str:
    return str(getattr(settings, "DEV_OTP_FALLBACK_CODE", "") or "").strip()


def dev_svt_fallback_code() -> str:
    return str(getattr(settings, "DEV_SVT_FALLBACK_CODE", "") or "").strip()


def dev_demo_svt_codes() -> list[str]:
    from apps.security.demo_svt_codes import get_dev_demo_svt_codes

    return get_dev_demo_svt_codes()
