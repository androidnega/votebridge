"""Development-only request logging for the Arkesel USSD callback."""

import json
import logging
from datetime import datetime, timezone
from urllib.parse import parse_qs

from django.conf import settings

logger = logging.getLogger("votebridge")

DEBUG_PREFIX = "[USSD CALLBACK DEBUG]"
SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "x-arkesel-secret",
        "x-api-key",
        "x-csrf-token",
    }
)


def log_incoming_callback(request) -> None:
    """Log callback request metadata when DEBUG=True."""
    if not settings.DEBUG:
        return

    content_type = request.content_type or ""
    raw_body = _read_raw_body(request)
    parsed_payload = _parse_payload(request, content_type, raw_body)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "http_method": request.method,
        "headers": _sanitize_headers(request),
        "content_type": content_type,
        "raw_body": raw_body,
        "parsed_payload": parsed_payload,
        "client_ip": _client_ip(request),
    }
    logger.info("%s %s", DEBUG_PREFIX, json.dumps(entry, default=str))


def _read_raw_body(request) -> str:
    body = getattr(request, "body", b"") or b""
    if not body:
        return ""
    return body.decode("utf-8", errors="replace")


def _sanitize_headers(request) -> dict:
    headers = {}
    for key, value in request.headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            headers[key] = "[REDACTED]"
        else:
            headers[key] = value
    return headers


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _parse_payload(request, content_type: str, raw_body: str) -> dict:
    if "application/json" in content_type:
        try:
            return json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            return {"_parse_error": "invalid_json"}

    form_data = _form_data(request)
    if form_data:
        return form_data

    if "application/x-www-form-urlencoded" in content_type and raw_body:
        parsed = parse_qs(raw_body, keep_blank_values=True)
        return {
            key: values[0] if len(values) == 1 else values
            for key, values in parsed.items()
        }

    return {}


def _form_data(request) -> dict:
    raw = getattr(request, "data", None)
    if raw:
        if hasattr(raw, "get"):
            return {key: raw.get(key) for key in raw.keys()}
        if hasattr(raw, "dict"):
            return raw.dict()
        return dict(raw)
    if request.POST:
        return dict(request.POST)
    return {}
