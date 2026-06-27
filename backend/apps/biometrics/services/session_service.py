import secrets
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from apps.accounts.models import User
from apps.biometrics.constants import HIGH_ASSURANCE_CACHE_PREFIX
from apps.biometrics.services.policy_service import biometric_policy_service
from core.exceptions import ValidationError


class BiometricSessionService:
    """High Assurance Session — short-lived elevation after biometric verification."""

    def issue_session(self, user: User) -> dict:
        policy = biometric_policy_service.get_policy()
        ttl_minutes = policy.get("session_timeout_minutes", 15)
        ttl_seconds = ttl_minutes * 60
        token = secrets.token_urlsafe(32)
        cache_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{token}"
        expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
        cache.set(cache_key, str(user.uuid), ttl_seconds)
        return {
            "high_assurance_token": token,
            "expires_at": expires_at.isoformat(),
            "expires_in_seconds": ttl_seconds,
        }

    def validate_session(self, user: User, token: str) -> None:
        cache_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{token}"
        stored = cache.get(cache_key)
        if not stored or str(stored) != str(user.uuid):
            raise ValidationError(
                message="High assurance biometric session is required or has expired.",
                code="biometric_session_required",
            )

    def consume_session(self, user: User, token: str) -> None:
        self.validate_session(user, token)
        cache.delete(f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{token}")

    def has_active_session(self, user: User) -> bool:
        pattern = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:"
        # Django cache doesn't support key scan; track latest token on issue
        latest_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:latest"
        token = cache.get(latest_key)
        if not token:
            return False
        return cache.get(f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{token}") is not None

    def register_latest_token(self, user: User, token: str, ttl_seconds: int) -> None:
        cache.set(f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:latest", token, ttl_seconds)
        cache.set(
            f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:meta",
            {"expires_in_seconds": ttl_seconds, "issued_at": timezone.now().isoformat()},
            ttl_seconds,
        )

    def get_session_status(self, user: User, token: str | None = None) -> dict:
        policy = biometric_policy_service.get_policy()
        if not policy.get("enable_face_verification"):
            return {"active": False, "enabled": False}

        from apps.trusted_devices.services.policy_service import trusted_device_policy_service

        if not trusted_device_policy_service.get_policy().get("enable_high_assurance_indicator", True):
            return {"active": False, "enabled": False}

        latest_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:latest"
        active_token = token or cache.get(latest_key)
        if not active_token:
            return {
                "active": False,
                "enabled": True,
                "status": "standard",
                "remaining_seconds": 0,
                "protected_actions_available": False,
            }

        cache_key = f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:{active_token}"
        if not cache.get(cache_key):
            return {
                "active": False,
                "enabled": True,
                "status": "expired",
                "remaining_seconds": 0,
                "protected_actions_available": False,
            }

        meta = cache.get(f"{HIGH_ASSURANCE_CACHE_PREFIX}{user.uuid}:meta") or {}
        ttl = int(meta.get("expires_in_seconds", policy.get("session_timeout_minutes", 15) * 60))

        return {
            "active": True,
            "enabled": True,
            "status": "high_assurance",
            "remaining_seconds": ttl,
            "protected_actions_available": True,
            "protected_actions": [
                "strongroom_access",
                "result_certification",
                "election_deletion",
                "system_control_access",
            ],
        }


biometric_session_service = BiometricSessionService()
