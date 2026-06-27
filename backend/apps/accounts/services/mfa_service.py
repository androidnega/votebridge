import logging

from apps.accounts.models import MFALog, User
from apps.accounts.repositories.auth_repository import MFALogRepository

logger = logging.getLogger("votebridge")


class MFAService:
    """Audit logging for authentication and MFA events."""

    def __init__(self, repository: MFALogRepository | None = None):
        self.repository = repository or MFALogRepository()

    def log(
        self,
        event_type: str,
        user: User | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
        browser_fingerprint: str | None = None,
    ) -> MFALog:
        metadata = metadata or {}
        mfa_log = self.repository.create(
            user=user,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent or "",
            metadata=metadata,
        )
        try:
            from apps.security.services.monitoring_service import monitoring_service

            monitoring_service.record_event(
                event_type=event_type,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                browser_fingerprint=browser_fingerprint,
                metadata=metadata,
                election_uuid=metadata.get("election_uuid"),
            )
        except Exception:
            logger.exception("Failed to record monitoring event for %s", event_type)
        return mfa_log

    def list_logs(self, user: User | None = None, limit: int = 50):
        if user:
            return self.repository.list_for_user(user, limit=limit)
        return self.repository.list_recent(limit=limit)
