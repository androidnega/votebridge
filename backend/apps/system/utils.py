from django.core.cache import cache
from django.core.signing import BadSignature, Signer

_signer = Signer(salt="votebridge.system.secrets")


def mask_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"


def encrypt_secret(value: str) -> str:
    return _signer.sign(value)


def decrypt_secret(value: str) -> str:
    try:
        return _signer.unsign(value)
    except BadSignature as exc:
        raise ValueError("Invalid encrypted secret") from exc


def mask_config(config: dict | None) -> dict:
    if not config:
        return {}
    sensitive_keys = {
        "api_key",
        "vas_key",
        "password",
        "secret",
        "webhook_secret",
        "auth_token",
        "smtp_password",
    }
    masked = {}
    for key, val in config.items():
        if key in sensitive_keys and val:
            masked[key] = "***"
        else:
            masked[key] = val
    return masked


def invalidate_settings_cache():
    cache.delete_many(
        [
            "system:settings:all",
            "system:maintenance",
            "system:feature_flags",
            "system:institution",
            "system:public_branding",
        ]
    )
