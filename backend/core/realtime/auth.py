"""JWT authentication middleware for Django Channels WebSockets."""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _get_user_from_token(token: str):
    from django.conf import settings
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from rest_framework_simplejwt.tokens import AccessToken

    from apps.accounts.models import User

    try:
        validated = AccessToken(token)
        claim = settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id")
        user_uuid = validated[claim]
        return User.objects.select_related("role").get(uuid=user_uuid)
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Resolve scope user from ?token=<JWT access token> query parameter."""

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if token:
            scope["user"] = await _get_user_from_token(token)
        elif scope.get("user") is None:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)
