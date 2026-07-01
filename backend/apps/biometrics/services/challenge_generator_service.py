import logging
import random
import secrets

from django.core.cache import cache

from apps.accounts.models import Role, User
from apps.biometrics.constants import (
    CHALLENGE_CACHE_PREFIX,
    CHALLENGE_LABELS,
    CHALLENGE_TTL_SECONDS,
    VERIFICATION_CHALLENGE_TYPES,
)
from apps.system.services.feature_flag_service import feature_flag_service
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")


class ChallengeGeneratorService:
    """Randomly selects and tracks active liveness challenges."""

    def _enabled_challenges(self) -> list[str]:
        from apps.biometrics.services.policy_service import biometric_policy_service

        policy = biometric_policy_service.get_policy()
        if not policy.get("enable_blink_challenge", True):
            return ["blink_once"]

        return list(VERIFICATION_CHALLENGE_TYPES)

    def generate(self, user: User) -> dict:
        if not feature_flag_service.is_enabled("future_biometrics"):
            raise ValidationError(message="Biometrics module is disabled.", code="biometrics_disabled")

        pool = self._enabled_challenges()
        challenge_type = random.choice(pool)
        challenge_id = secrets.token_urlsafe(16)
        cache_key = f"{CHALLENGE_CACHE_PREFIX}{challenge_id}"
        cache.set(
            cache_key,
            {
                "user_uuid": str(user.uuid),
                "challenge_type": challenge_type,
            },
            CHALLENGE_TTL_SECONDS,
        )
        return {
            "challenge_id": challenge_id,
            "challenge_type": challenge_type,
            "instruction": CHALLENGE_LABELS.get(challenge_type, challenge_type),
            "expires_in_seconds": CHALLENGE_TTL_SECONDS,
        }

    def get_challenge(self, challenge_id: str) -> dict | None:
        return cache.get(f"{CHALLENGE_CACHE_PREFIX}{challenge_id}")

    def consume_challenge(self, challenge_id: str) -> dict | None:
        key = f"{CHALLENGE_CACHE_PREFIX}{challenge_id}"
        data = cache.get(key)
        if data:
            cache.delete(key)
        return data


challenge_generator_service = ChallengeGeneratorService()
