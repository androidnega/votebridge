import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import MFALog, Session, User
from apps.accounts.repositories.auth_repository import SessionRepository
from apps.accounts.services.mfa_service import MFAService

logger = logging.getLogger("votebridge")


class SessionService:
    """JWT session lifecycle management."""

    def __init__(
        self,
        session_repository: SessionRepository | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.session_repository = session_repository or SessionRepository()
        self.mfa_service = mfa_service or MFAService()

    def create_session(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[Session, dict]:
        lifetime_days = self.session_repository.get_session_lifetime_days()
        expires_at = timezone.now() + timedelta(days=lifetime_days)

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role.name
        refresh["user_uuid"] = str(user.uuid)

        session = self.session_repository.create(
            user=user,
            refresh_token_jti=str(refresh["jti"]),
            ip_address=ip_address,
            user_agent=user_agent or "",
            expires_at=expires_at,
            last_activity_at=timezone.now(),
        )

        refresh["session_uuid"] = str(session.uuid)

        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        logger.info("Session created for user %s", user.uuid)
        return session, tokens

    def get_active_session(self, jti: str) -> Session | None:
        session = self.session_repository.get_by_jti(jti)
        if not session or not session.is_active:
            return None
        if timezone.now() > session.expires_at:
            return None
        return session

    def touch_session(self, session: Session) -> Session:
        return self.session_repository.update(
            session,
            last_activity_at=timezone.now(),
        )

    def revoke_session(
        self,
        session_uuid,
        user: User | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        session = self.session_repository.get_by_uuid(session_uuid)
        if not session:
            from core.exceptions import NotFoundError

            raise NotFoundError(message="Session not found.", code="session_not_found")

        if user and session.user_id != user.id:
            from core.exceptions import PermissionDeniedError

            raise PermissionDeniedError(
                message="You cannot revoke this session.",
                code="session_revoke_denied",
            )

        session = self.session_repository.revoke(session)
        self.mfa_service.log(
            event_type=MFALog.EventType.SESSION_REVOKED,
            user=session.user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_uuid": str(session.uuid)},
        )
        return session

    def logout(
        self,
        jti: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        session = self.session_repository.get_by_jti(jti)
        if session and session.is_active:
            self.session_repository.revoke(session)
            self.mfa_service.log(
                event_type=MFALog.EventType.LOGOUT,
                user=session.user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"session_uuid": str(session.uuid)},
            )

    def list_sessions(self, user: User):
        return self.session_repository.list_active_for_user(user)

    def refresh_tokens(
        self,
        refresh_token: RefreshToken,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        jti = str(refresh_token["jti"])
        session = self.get_active_session(jti)
        if not session:
            from core.exceptions import AuthenticationError

            raise AuthenticationError(
                message="Session is invalid or expired.",
                code="session_invalid",
            )

        self.touch_session(session)
        self.mfa_service.log(
            event_type=MFALog.EventType.TOKEN_REFRESH,
            user=session.user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_uuid": str(session.uuid)},
        )

        return {
            "access": str(refresh_token.access_token),
            "refresh": str(refresh_token),
        }
