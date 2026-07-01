import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.notifications.models import CommunicationProvider, DeliveryLog, NotificationTemplate
from apps.notifications.providers.base import get_provider_instance, render_template_text
from apps.notifications.repositories.notification_repository import (
    CommunicationProviderRepository,
    DeliveryLogRepository,
    InAppNotificationRepository,
    NotificationTemplateRepository,
)
from apps.system.services.feature_flag_service import feature_flag_service
from core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger("votebridge")

RETRY_DELAY_MINUTES = 5


class CommunicationService:
    """Central hub for all outbound communications."""

    def __init__(
        self,
        template_repository: NotificationTemplateRepository | None = None,
        delivery_repository: DeliveryLogRepository | None = None,
        in_app_repository: InAppNotificationRepository | None = None,
        provider_repository: CommunicationProviderRepository | None = None,
    ):
        self.template_repository = template_repository or NotificationTemplateRepository()
        self.delivery_repository = delivery_repository or DeliveryLogRepository()
        self.in_app_repository = in_app_repository or InAppNotificationRepository()
        self.provider_repository = provider_repository or CommunicationProviderRepository()

    def dispatch(
        self,
        *,
        template_code: str,
        channel: str,
        recipient: str,
        context: dict | None = None,
        user=None,
        actor=None,
        metadata: dict | None = None,
    ) -> DeliveryLog:
        """Send a templated message on a single channel."""
        template = self.template_repository.get_by_code(template_code)
        if not template:
            raise NotFoundError(
                message=f"Template '{template_code}' not found.",
                code="template_not_found",
            )

        context = context or {}
        rendered = self._render_template(template, channel, context)

        return self._create_and_send(
            channel=channel,
            recipient=recipient,
            subject=rendered["subject"],
            body=rendered["body"],
            body_html=rendered.get("body_html", ""),
            in_app_title=rendered.get("in_app_title", ""),
            in_app_body=rendered.get("in_app_body", ""),
            template=template,
            template_code=template_code,
            context=context,
            user=user,
            actor=actor,
            metadata=metadata,
        )

    def dispatch_multi(
        self,
        *,
        template_code: str,
        channels: list[str],
        recipient: str,
        context: dict | None = None,
        user=None,
        actor=None,
        metadata: dict | None = None,
    ) -> list[DeliveryLog]:
        logs = []
        for channel in channels:
            logs.append(
                self.dispatch(
                    template_code=template_code,
                    channel=channel,
                    recipient=recipient,
                    context=context,
                    user=user,
                    actor=actor,
                    metadata=metadata,
                )
            )
        return logs

    def send_raw(
        self,
        *,
        channel: str,
        recipient: str,
        body: str,
        subject: str = "",
        body_html: str = "",
        user=None,
        actor=None,
        template_code: str = "",
        metadata: dict | None = None,
    ) -> DeliveryLog:
        """Send a pre-rendered message (e.g. OTP). All system sends must use this or dispatch."""
        return self._create_and_send(
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            body_html=body_html,
            template=None,
            template_code=template_code or "raw_message",
            context={},
            user=user,
            actor=actor,
            metadata=metadata,
        )

    def _render_template(self, template: NotificationTemplate, channel: str, context: dict) -> dict:
        if channel == DeliveryLog.Channel.SMS:
            return {
                "subject": "",
                "body": render_template_text(template.sms_body or template.body_text, context),
            }
        if channel == DeliveryLog.Channel.EMAIL:
            return {
                "subject": render_template_text(template.subject, context),
                "body": render_template_text(template.body_text, context),
                "body_html": render_template_text(template.body_html, context),
            }
        if channel == DeliveryLog.Channel.IN_APP:
            return {
                "subject": "",
                "body": render_template_text(template.in_app_body or template.body_text, context),
                "in_app_title": render_template_text(template.in_app_title or template.name, context),
                "in_app_body": render_template_text(template.in_app_body or template.body_text, context),
            }
        raise ValidationError(message=f"Unsupported channel: {channel}", code="invalid_channel")

    def _create_and_send(
        self,
        *,
        channel: str,
        recipient: str,
        subject: str,
        body: str,
        body_html: str = "",
        in_app_title: str = "",
        in_app_body: str = "",
        template: NotificationTemplate | None,
        template_code: str,
        context: dict,
        user=None,
        actor=None,
        metadata: dict | None = None,
    ) -> DeliveryLog:
        if not feature_flag_service.is_channel_enabled(channel):
            logger.info("Skipping %s delivery — channel disabled by feature flag", channel)
            raise ValidationError(
                message=f"{channel.upper()} notifications are currently disabled.",
                code="channel_disabled",
            )

        meta = dict(metadata or {})
        if body_html:
            meta["body_html"] = body_html

        delivery_log = self.delivery_repository.create(
            user=user,
            recipient=recipient,
            channel=channel,
            template=template,
            template_code=template_code,
            subject=subject,
            body_snapshot=body,
            context_data=context,
            status=DeliveryLog.Status.PENDING,
            metadata=meta,
        )

        self._record_audit(actor, delivery_log, "communication_queued")

        try:
            return self._deliver(delivery_log, in_app_title=in_app_title, in_app_body=in_app_body)
        except Exception as exc:
            logger.exception("Delivery failed for %s", delivery_log.uuid)
            self._handle_failure(delivery_log, str(exc))
            raise

    def _deliver(self, delivery_log: DeliveryLog, in_app_title: str = "", in_app_body: str = "") -> DeliveryLog:
        delivery_log.status = DeliveryLog.Status.PROCESSING
        delivery_log.save(update_fields=["status"])

        if delivery_log.channel == DeliveryLog.Channel.IN_APP:
            return self._deliver_in_app(delivery_log, in_app_title, in_app_body)

        provider_type = (
            CommunicationProvider.ProviderType.ARKESEL_SMS
            if delivery_log.channel == DeliveryLog.Channel.SMS
            else CommunicationProvider.ProviderType.SMTP_EMAIL
        )
        provider_record = self.provider_repository.get_default_for_type(provider_type)
        provider = get_provider_instance(provider_record, provider_type)

        delivery_log.provider = provider_record
        delivery_log.provider_name = provider_record.name if provider_record else provider_type
        delivery_log.save(update_fields=["provider", "provider_name"])

        response = provider.send(delivery_log)
        delivery_log.status = DeliveryLog.Status.DELIVERED
        delivery_log.delivered_at = timezone.now()
        delivery_log.provider_response = response
        delivery_log.save(
            update_fields=["status", "delivered_at", "provider_response"]
        )

        if provider_record:
            provider_record.connection_status = CommunicationProvider.ConnectionStatus.CONNECTED
            provider_record.last_success_at = timezone.now()
            provider_record.last_error = ""
            provider_record.save(
                update_fields=["connection_status", "last_success_at", "last_error"]
            )

        self._record_audit(None, delivery_log, "communication_delivered")
        self._broadcast_delivery(delivery_log)
        return delivery_log

    def _deliver_in_app(
        self,
        delivery_log: DeliveryLog,
        title: str,
        body: str,
    ) -> DeliveryLog:
        if not delivery_log.user:
            raise ValidationError(
                message="In-app notifications require a user.",
                code="user_required",
            )

        notification = self.in_app_repository.create(
            user=delivery_log.user,
            delivery_log=delivery_log,
            title=title or delivery_log.subject or "Notification",
            body=body or delivery_log.body_snapshot,
            category=delivery_log.template_code,
            metadata=delivery_log.context_data,
        )

        delivery_log.status = DeliveryLog.Status.DELIVERED
        delivery_log.delivered_at = timezone.now()
        delivery_log.provider_name = "in_app"
        delivery_log.provider_response = {"notification_uuid": str(notification.uuid)}
        delivery_log.save(
            update_fields=["status", "delivered_at", "provider_name", "provider_response"]
        )

        self._broadcast_in_app(notification)
        self._broadcast_delivery(delivery_log)
        return delivery_log

    def _handle_failure(self, delivery_log: DeliveryLog, error_message: str) -> None:
        delivery_log.retry_count += 1
        delivery_log.error_message = error_message
        delivery_log.failed_at = timezone.now()

        if delivery_log.retry_count < delivery_log.max_retries:
            delivery_log.status = DeliveryLog.Status.RETRYING
            delivery_log.next_retry_at = timezone.now() + timedelta(minutes=RETRY_DELAY_MINUTES)
        else:
            delivery_log.status = DeliveryLog.Status.FAILED

        delivery_log.save(
            update_fields=[
                "retry_count",
                "error_message",
                "failed_at",
                "status",
                "next_retry_at",
            ]
        )

        if delivery_log.provider:
            delivery_log.provider.connection_status = CommunicationProvider.ConnectionStatus.ERROR
            delivery_log.provider.last_error = error_message
            delivery_log.provider.last_error_at = timezone.now()
            delivery_log.provider.save(
                update_fields=["connection_status", "last_error", "last_error_at"]
            )

        self._record_audit(None, delivery_log, "communication_failed")
        self._broadcast_delivery(delivery_log)

    def retry_delivery(self, delivery_log: DeliveryLog) -> DeliveryLog:
        if delivery_log.status not in {
            DeliveryLog.Status.FAILED,
            DeliveryLog.Status.RETRYING,
            DeliveryLog.Status.PENDING,
        }:
            raise ValidationError(message="Delivery cannot be retried.", code="invalid_status")

        delivery_log.status = DeliveryLog.Status.PENDING
        delivery_log.save(update_fields=["status"])
        return self._deliver(delivery_log)

    def process_queue(self, limit: int = 50) -> dict:
        """Process pending/retrying messages. Celery-ready."""
        pending = self.delivery_repository.get_pending_for_retry(limit=limit)
        processed = succeeded = failed = 0

        for log in pending:
            if not feature_flag_service.is_channel_enabled(log.channel):
                logger.info("Skipping queued %s delivery — channel disabled", log.channel)
                continue
            processed += 1
            try:
                self._deliver(log)
                succeeded += 1
            except Exception as exc:
                self._handle_failure(log, str(exc))
                failed += 1

        return {"processed": processed, "succeeded": succeeded, "failed": failed}

    def get_dashboard(self) -> dict:
        stats = self.delivery_repository.dashboard_stats()
        providers = list(self.provider_repository.get_queryset().order_by("provider_type"))
        stats["providers"] = [
            {
                "uuid": str(p.uuid),
                "name": p.name,
                "provider_type": p.provider_type,
                "is_active": p.is_active,
                "connection_status": p.connection_status,
                "last_success_at": p.last_success_at,
                "last_error": p.last_error,
                "last_error_at": p.last_error_at,
            }
            for p in providers
        ]
        return stats

    def test_provider(self, provider_uuid) -> dict:
        provider_record = self.provider_repository.get_by_uuid(provider_uuid)
        if not provider_record:
            raise NotFoundError(message="Provider not found.", code="provider_not_found")

        provider = get_provider_instance(provider_record, provider_record.provider_type)
        result = provider.test_connection()

        if result.get("success"):
            provider_record.connection_status = CommunicationProvider.ConnectionStatus.CONNECTED
            provider_record.last_success_at = timezone.now()
            provider_record.last_error = ""
        else:
            provider_record.connection_status = CommunicationProvider.ConnectionStatus.ERROR
            provider_record.last_error = result.get("message", "Connection test failed.")
            provider_record.last_error_at = timezone.now()

        provider_record.save(
            update_fields=["connection_status", "last_success_at", "last_error", "last_error_at"]
        )
        return result

    def _record_audit(self, actor, delivery_log: DeliveryLog, action: str) -> None:
        try:
            from apps.security.services.monitoring_service import monitoring_service

            monitoring_service.record_event(
                event_type="admin_action",
                user=actor or delivery_log.user,
                metadata={
                    "action": action,
                    "delivery_uuid": str(delivery_log.uuid),
                    "channel": delivery_log.channel,
                    "template_code": delivery_log.template_code,
                    "recipient": delivery_log.recipient,
                    "status": delivery_log.status,
                },
            )
        except Exception:
            logger.exception("Failed to record communication audit event")

    def _broadcast_delivery(self, delivery_log: DeliveryLog) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            transaction.on_commit(
                lambda: realtime_broadcast_service.communication_delivery_updated(delivery_log)
            )
        except Exception:
            logger.debug("Realtime broadcast skipped for delivery %s", delivery_log.uuid)

    def _broadcast_in_app(self, notification) -> None:
        try:
            from core.realtime.broadcasting import realtime_broadcast_service

            transaction.on_commit(
                lambda: realtime_broadcast_service.in_app_notification_created(notification)
            )
        except Exception:
            logger.debug("Realtime broadcast skipped for notification %s", notification.uuid)


communication_service = CommunicationService()
