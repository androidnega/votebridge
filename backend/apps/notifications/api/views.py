from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import DeliveryLog, InAppNotification, NotificationTemplate
from apps.notifications.permissions import (
    CanManageCommunicationSettings,
    CanManageCommunications,
    CanViewCommunications,
    CanViewOwnNotifications,
)
from apps.notifications.repositories.notification_repository import (
    CommunicationProviderRepository,
    DeliveryLogRepository,
    InAppNotificationRepository,
    NotificationTemplateRepository,
)
from apps.notifications.services.communication_service import communication_service
from core.exceptions import NotFoundError


def _serialize_delivery(log: DeliveryLog) -> dict:
    return {
        "uuid": str(log.uuid),
        "recipient": log.recipient,
        "channel": log.channel,
        "template_code": log.template_code,
        "provider_name": log.provider_name,
        "status": log.status,
        "subject": log.subject,
        "retry_count": log.retry_count,
        "error_message": log.error_message,
        "created_at": log.created_at,
        "delivered_at": log.delivered_at,
        "failed_at": log.failed_at,
    }


def _serialize_notification(n: InAppNotification) -> dict:
    return {
        "uuid": str(n.uuid),
        "title": n.title,
        "body": n.body,
        "category": n.category,
        "is_read": n.is_read,
        "is_archived": n.is_archived,
        "read_at": n.read_at,
        "created_at": n.created_at,
        "metadata": n.metadata,
    }


def _serialize_template(t: NotificationTemplate) -> dict:
    return {
        "uuid": str(t.uuid),
        "code": t.code,
        "name": t.name,
        "channel": t.channel,
        "subject": t.subject,
        "body_text": t.body_text,
        "body_html": t.body_html,
        "sms_body": t.sms_body,
        "in_app_title": t.in_app_title,
        "in_app_body": t.in_app_body,
        "placeholders": t.placeholders,
        "is_active": t.is_active,
    }


def _serialize_provider(p) -> dict:
    return {
        "uuid": str(p.uuid),
        "name": p.name,
        "provider_type": p.provider_type,
        "is_active": p.is_active,
        "is_default": p.is_default,
        "connection_status": p.connection_status,
        "last_success_at": p.last_success_at,
        "last_error": p.last_error,
        "last_error_at": p.last_error_at,
        "config": {k: "***" if k in {"api_key", "password"} else v for k, v in (p.config or {}).items()},
    }


class CommunicationDashboardView(APIView):
    permission_classes = [CanViewCommunications]

    def get(self, request):
        return Response({"success": True, "data": communication_service.get_dashboard()})


class DeliveryLogListView(APIView):
    permission_classes = [CanViewCommunications]

    def get(self, request):
        channel = request.query_params.get("channel")
        log_status = request.query_params.get("status")
        search = request.query_params.get("search", "").strip() or None
        limit = min(int(request.query_params.get("limit", 50)), 100)
        offset = int(request.query_params.get("offset", 0))

        repo = DeliveryLogRepository()
        items, total = repo.list_filtered(
            channel=channel,
            status=log_status,
            search=search,
            limit=limit,
            offset=offset,
        )
        return Response(
            {
                "success": True,
                "data": {
                    "items": [_serialize_delivery(i) for i in items],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                },
            }
        )


class QueueProcessView(APIView):
    permission_classes = [CanManageCommunicationSettings]

    def post(self, request):
        limit = min(int(request.data.get("limit", 50)), 200)
        result = communication_service.process_queue(limit=limit)
        return Response({"success": True, "data": result})


class DeliveryRetryView(APIView):
    permission_classes = [CanManageCommunicationSettings]

    def post(self, request, log_uuid):
        repo = DeliveryLogRepository()
        log = repo.get_by_uuid(log_uuid)
        if not log:
            raise NotFoundError(message="Delivery log not found.", code="not_found")
        try:
            updated = communication_service.retry_delivery(log)
            return Response({"success": True, "data": _serialize_delivery(updated)})
        except Exception as exc:
            return Response(
                {"success": False, "error": {"code": "retry_failed", "message": str(exc)}},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class TemplateListView(APIView):
    permission_classes = [CanViewCommunications]

    def get(self, request):
        repo = NotificationTemplateRepository()
        templates = repo.list_active()
        return Response(
            {"success": True, "data": [_serialize_template(t) for t in templates]}
        )


class ProviderListView(APIView):
    permission_classes = [CanViewCommunications]

    def get(self, request):
        repo = CommunicationProviderRepository()
        providers = repo.get_queryset().order_by("provider_type")
        return Response(
            {"success": True, "data": [_serialize_provider(p) for p in providers]}
        )


class ProviderTestView(APIView):
    permission_classes = [CanManageCommunicationSettings]

    def post(self, request, provider_uuid):
        result = communication_service.test_provider(provider_uuid)
        return Response({"success": True, "data": result})


class TestMessageView(APIView):
    permission_classes = [CanManageCommunicationSettings]

    def post(self, request):
        channel = request.data.get("channel", "email")
        recipient = request.data.get("recipient", "").strip()
        template_code = request.data.get("template_code", "test_message")
        if not recipient:
            return Response(
                {
                    "success": False,
                    "error": {"code": "validation_error", "message": "recipient is required."},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        log = communication_service.dispatch(
            template_code=template_code,
            channel=channel,
            recipient=recipient,
            context=request.data.get("context", {}),
            user=request.user,
            actor=request.user,
        )
        return Response({"success": True, "data": _serialize_delivery(log)})


class NotificationCenterView(APIView):
    permission_classes = [CanViewOwnNotifications]

    def get(self, request):
        archived = request.query_params.get("archived", "false").lower() == "true"
        unread_only = request.query_params.get("unread", "false").lower() == "true"
        limit = min(int(request.query_params.get("limit", 50)), 100)
        offset = int(request.query_params.get("offset", 0))

        repo = InAppNotificationRepository()
        items, total = repo.list_for_user(
            request.user,
            archived=archived,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
        )
        unread_count = repo.unread_count(request.user)
        return Response(
            {
                "success": True,
                "data": {
                    "items": [_serialize_notification(n) for n in items],
                    "total": total,
                    "unread_count": unread_count,
                    "limit": limit,
                    "offset": offset,
                },
            }
        )


class NotificationMarkReadView(APIView):
    permission_classes = [CanViewOwnNotifications]

    def post(self, request, notification_uuid):
        repo = InAppNotificationRepository()
        notification = repo.get_for_user(request.user, notification_uuid)
        if not notification:
            raise NotFoundError(message="Notification not found.", code="not_found")
        repo.mark_read(notification)
        return Response({"success": True, "data": _serialize_notification(notification)})


class NotificationMarkAllReadView(APIView):
    permission_classes = [CanViewOwnNotifications]

    def post(self, request):
        repo = InAppNotificationRepository()
        count = repo.mark_all_read(request.user)
        return Response({"success": True, "data": {"marked_read": count}})


class NotificationArchiveView(APIView):
    permission_classes = [CanViewOwnNotifications]

    def post(self, request, notification_uuid):
        repo = InAppNotificationRepository()
        notification = repo.get_for_user(request.user, notification_uuid)
        if not notification:
            raise NotFoundError(message="Notification not found.", code="not_found")
        repo.archive(notification)
        return Response({"success": True, "data": _serialize_notification(notification)})


class NotificationDeleteView(APIView):
    permission_classes = [CanViewOwnNotifications]

    def delete(self, request, notification_uuid):
        repo = InAppNotificationRepository()
        notification = repo.get_for_user(request.user, notification_uuid)
        if not notification:
            raise NotFoundError(message="Notification not found.", code="not_found")
        repo.soft_delete(notification)
        return Response({"success": True, "data": {"deleted": True}})
