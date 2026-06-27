from datetime import timedelta

from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services.session_service import SessionService
from core.exceptions import AuthenticationError


class TokenService:
    """JWT token refresh with session validation."""

    def __init__(self, session_service: SessionService | None = None):
        self.session_service = session_service or SessionService()

    def refresh(
        self,
        refresh_token_str: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        try:
            refresh = RefreshToken(refresh_token_str)
        except TokenError as exc:
            raise AuthenticationError(
                message="Invalid or expired refresh token.",
                code="invalid_refresh_token",
            ) from exc

        return self.session_service.refresh_tokens(
            refresh_token=refresh,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def get_token_lifetime_seconds() -> dict:
        return {
            "access_lifetime_seconds": int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            ),
            "refresh_lifetime_seconds": int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            ),
        }
