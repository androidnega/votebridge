import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import Role
from apps.elections.repositories.election_repository import ElectionRepository
from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository
from core.realtime import groups

logger = logging.getLogger("votebridge")


def _user_role_name(user) -> str | None:
    if not user.is_authenticated or not hasattr(user, "role"):
        return None
    return user.role.name


class BaseRealtimeConsumer(AsyncWebsocketConsumer):
    """Shared connect/disconnect and event delivery for VoteBridge realtime feeds."""

    group_names: list[str] = []

    async def connect(self):
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user = user
        self.group_names = await self.resolve_groups()
        if not self.group_names:
            await self.close(code=4403)
            return

        for group_name in self.group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "event": "connection.established",
                    "data": {"status": "connected", "groups": self.group_names},
                    "timestamp": None,
                }
            )
        )
        snapshot = await self.build_snapshot()
        if snapshot:
            await self.send(
                text_data=json.dumps(
                    {
                        "event": "dashboard_stats",
                        "data": snapshot,
                        "timestamp": None,
                    }
                )
            )

    async def disconnect(self, close_code):
        for group_name in getattr(self, "group_names", []):
            await self.channel_layer.group_discard(group_name, self.channel_name)
        logger.info("WebSocket disconnected (%s) code=%s", self.__class__.__name__, close_code)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                payload = json.loads(text_data)
            except json.JSONDecodeError:
                return
            if payload.get("action") == "ping":
                await self.send(text_data=json.dumps({"event": "pong", "data": {}, "timestamp": None}))

    async def realtime_event(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": event["event_type"],
                    "data": event["payload"],
                    "timestamp": event.get("timestamp"),
                }
            )
        )

    async def resolve_groups(self) -> list[str]:
        return []

    async def build_snapshot(self) -> dict | None:
        return None


class DashboardConsumer(BaseRealtimeConsumer):
    """Role-aware dashboard feed for admin and student overview widgets."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return [groups.dashboard_admin()]
        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            return [groups.dashboard_student(self.user.uuid)]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.dashboard.services.dashboard_service import dashboard_service

        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return {"role": "admin", **dashboard_service.get_admin_overview()}
        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            return {"role": "student", **dashboard_service.get_student_overview(self.user)}
        return None


class ElectionConsumer(BaseRealtimeConsumer):
    """Per-election monitoring feed — status and aggregate ballot activity only."""

    async def resolve_groups(self) -> list[str]:
        election_uuid = self.scope["url_route"]["kwargs"].get("election_uuid")
        if not election_uuid:
            return []

        allowed = await self._can_access_election(election_uuid)
        if not allowed:
            return []
        return [groups.election(election_uuid)]

    @database_sync_to_async
    def _can_access_election(self, election_uuid) -> bool:
        role = _user_role_name(self.user)
        election = ElectionRepository().get_by_uuid(election_uuid)
        if not election:
            return False
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return True
        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            return VoterEligibilityRepository().is_user_eligible(election, self.user)
        return False

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.dashboard.services.dashboard_service import dashboard_service

        election_uuid = self.scope["url_route"]["kwargs"].get("election_uuid")
        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return dashboard_service.get_election_monitoring(election_uuid)
        return dashboard_service.get_student_election_status(self.user, election_uuid)


class SecurityConsumer(BaseRealtimeConsumer):
    """Realtime security alert feed for admin dashboards."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return [groups.security()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.dashboard.services.dashboard_service import dashboard_service

        return dashboard_service.get_security_feed_snapshot()


class FraudConsumer(BaseRealtimeConsumer):
    """Realtime fraud case feed for investigation dashboards."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return [groups.fraud()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.dashboard.services.dashboard_service import dashboard_service

        return dashboard_service.get_fraud_feed_snapshot()


class ResultsConsumer(BaseRealtimeConsumer):
    """Realtime results certification and publication feed."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return [groups.results()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.results.repositories.election_result_repository import ElectionResultRepository

        repo = ElectionResultRepository()
        certification = [
            {
                "uuid": str(r.uuid),
                "election_uuid": str(r.election.uuid),
                "election_title": r.election.title,
                "result_status": r.status,
            }
            for r in repo.list_certification_queue()[:10]
        ]
        publication = [
            {
                "uuid": str(r.uuid),
                "election_uuid": str(r.election.uuid),
                "election_title": r.election.title,
                "result_status": r.status,
            }
            for r in repo.list_publication_queue()[:10]
        ]
        return {"certification_queue": certification, "publication_queue": publication}


class StrongroomConsumer(BaseRealtimeConsumer):
    """Realtime strongroom integrity feed — Super Admin platform oversight only."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return [groups.strongroom()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.strongroom.repositories.strongroom_repository import (
            ElectionSealRepository,
            IntegrityVerificationRepository,
        )

        seals = ElectionSealRepository().get_queryset().order_by("-updated_at")[:10]
        recent = IntegrityVerificationRepository()
        return {
            "seals": [
                {
                    "election_uuid": str(s.election.uuid),
                    "election_title": s.election.title,
                    "seal_status": s.status,
                    "verification_hash": s.verification_hash,
                }
                for s in seals
            ],
        }


class CommunicationsConsumer(BaseRealtimeConsumer):
    """Realtime communication delivery feed — platform operations (Super Admin)."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return [groups.communications()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.notifications.services.communication_service import communication_service

        return communication_service.get_dashboard()


class NotificationConsumer(BaseRealtimeConsumer):
    """Realtime in-app notification feed for authenticated users."""

    async def resolve_groups(self) -> list[str]:
        return [groups.user_notifications(self.user.uuid)]

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.notifications.repositories.notification_repository import (
            InAppNotificationRepository,
        )

        repo = InAppNotificationRepository()
        items, total = repo.list_for_user(self.user, limit=10, offset=0)
        return {
            "unread_count": repo.unread_count(self.user),
            "items": [
                {
                    "uuid": str(n.uuid),
                    "title": n.title,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat(),
                }
                for n in items
            ],
            "total": total,
        }


class UssdConsumer(BaseRealtimeConsumer):
    """Realtime USSD session monitor — platform operations (Super Admin)."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return [groups.ussd()]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.ussd.repositories.ussd_repository import USSDSessionRepository

        return USSDSessionRepository().dashboard_stats()


class OperationsConsumer(BaseRealtimeConsumer):
    """Enterprise Operations Center — platform-wide operational feeds (Super Admin)."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return [
                groups.operations(),
                groups.security(),
                groups.fraud(),
                groups.communications(),
                groups.ussd(),
                groups.results(),
            ]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.operations.services.operations_service import operations_dashboard_service

        return operations_dashboard_service.get_overview()


class AnalyticsConsumer(BaseRealtimeConsumer):
    """Enterprise Analytics — read-only intelligence feed."""

    async def resolve_groups(self) -> list[str]:
        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return [
                groups.analytics(),
                groups.security(),
                groups.fraud(),
                groups.results(),
                groups.communications(),
                groups.ussd(),
                groups.operations(),
            ]
        if role == Role.Name.ADMIN:
            return [
                groups.analytics(),
                groups.security(),
                groups.fraud(),
                groups.results(),
            ]
        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            return [groups.dashboard_student(self.user.uuid)]
        return []

    @database_sync_to_async
    def build_snapshot(self) -> dict | None:
        from apps.analytics.services.analytics_service import analytics_dashboard_service

        role = _user_role_name(self.user)
        if role == Role.Name.SUPER_ADMIN:
            return analytics_dashboard_service.get_overview()
        if role == Role.Name.ADMIN:
            return analytics_dashboard_service.get_overview()
        from apps.analytics.services.analytics_service import analytics_student_service

        return analytics_student_service.get_personal_analytics(self.user)
