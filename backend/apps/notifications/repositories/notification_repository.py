from django.db import models
from django.db.models import Count, F, Q, QuerySet
from django.utils import timezone

from apps.notifications.models import (
    CommunicationProvider,
    DeliveryLog,
    InAppNotification,
    NotificationTemplate,
)


class NotificationTemplateRepository:
    def get_queryset(self) -> QuerySet[NotificationTemplate]:
        return NotificationTemplate.objects.all()

    def get_by_code(self, code: str) -> NotificationTemplate | None:
        return self.get_queryset().filter(code=code, is_active=True).first()

    def list_active(self) -> QuerySet[NotificationTemplate]:
        return self.get_queryset().filter(is_active=True).order_by("code")


class CommunicationProviderRepository:
    def get_queryset(self) -> QuerySet[CommunicationProvider]:
        return CommunicationProvider.objects.all()

    def get_default_for_type(self, provider_type: str) -> CommunicationProvider | None:
        return (
            self.get_queryset()
            .filter(provider_type=provider_type, is_active=True)
            .order_by("-is_default", "-updated_at")
            .first()
        )

    def get_sms_delivery_chain(self) -> list[CommunicationProvider]:
        """Primary Arkesel SMS, then Moolre SMS fallback when configured."""
        chain: list[CommunicationProvider] = []
        primary = self.get_default_for_type(CommunicationProvider.ProviderType.ARKESEL_SMS)
        fallback = self.get_default_for_type(CommunicationProvider.ProviderType.MOOLRE_SMS)
        if primary:
            chain.append(primary)
        if fallback and (not primary or fallback.pk != primary.pk):
            chain.append(fallback)
        return chain

    def get_by_uuid(self, provider_uuid) -> CommunicationProvider | None:
        return self.get_queryset().filter(uuid=provider_uuid).first()


class DeliveryLogRepository:
    def get_queryset(self) -> QuerySet[DeliveryLog]:
        return DeliveryLog.objects.select_related("template", "provider", "user")

    def create(self, **kwargs) -> DeliveryLog:
        return DeliveryLog.objects.create(**kwargs)

    def get_by_uuid(self, log_uuid) -> DeliveryLog | None:
        return self.get_queryset().filter(uuid=log_uuid).first()

    def list_filtered(
        self,
        *,
        channel: str | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DeliveryLog], int]:
        qs = self.get_queryset()
        if channel:
            qs = qs.filter(channel=channel)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(recipient__icontains=search)
                | Q(template_code__icontains=search)
                | Q(subject__icontains=search)
            )
        total = qs.count()
        return list(qs[offset : offset + limit]), total

    def get_pending_for_retry(self, limit: int = 50) -> list[DeliveryLog]:
        now = timezone.now()
        return list(
            self.get_queryset()
            .filter(
                status__in=[DeliveryLog.Status.PENDING, DeliveryLog.Status.RETRYING],
                retry_count__lt=F("max_retries"),
            )
            .filter(Q(next_retry_at__isnull=True) | Q(next_retry_at__lte=now))
            .order_by("created_at")[:limit]
        )

    def dashboard_stats(self) -> dict:
        qs = DeliveryLog.objects.all()
        today = timezone.now().date()
        by_status = dict(qs.values("status").annotate(c=Count("id")).values_list("status", "c"))
        by_channel = dict(
            qs.filter(status=DeliveryLog.Status.DELIVERED)
            .values("channel")
            .annotate(c=Count("id"))
            .values_list("channel", "c")
        )
        return {
            "total_messages": qs.count(),
            "sms_delivered": by_channel.get(DeliveryLog.Channel.SMS, 0),
            "email_delivered": by_channel.get(DeliveryLog.Channel.EMAIL, 0),
            "failed_messages": by_status.get(DeliveryLog.Status.FAILED, 0),
            "pending_queue": by_status.get(DeliveryLog.Status.PENDING, 0),
            "retry_queue": by_status.get(DeliveryLog.Status.RETRYING, 0),
            "notifications_sent_today": qs.filter(created_at__date=today).count(),
            "in_app_sent_today": qs.filter(
                channel=DeliveryLog.Channel.IN_APP,
                created_at__date=today,
            ).count(),
        }


class InAppNotificationRepository:
    def get_queryset_for_user(self, user) -> QuerySet[InAppNotification]:
        return InAppNotification.objects.filter(user=user, is_deleted=False)

    def list_for_user(
        self,
        user,
        *,
        archived: bool = False,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[InAppNotification], int]:
        qs = self.get_queryset_for_user(user).filter(is_archived=archived)
        if unread_only:
            qs = qs.filter(is_read=False)
        total = qs.count()
        return list(qs[offset : offset + limit]), total

    def unread_count(self, user) -> int:
        return self.get_queryset_for_user(user).filter(is_read=False, is_archived=False).count()

    def create(self, **kwargs) -> InAppNotification:
        return InAppNotification.objects.create(**kwargs)

    def get_for_user(self, user, notification_uuid) -> InAppNotification | None:
        return self.get_queryset_for_user(user).filter(uuid=notification_uuid).first()

    def mark_read(self, notification: InAppNotification) -> InAppNotification:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return notification

    def mark_all_read(self, user) -> int:
        return (
            self.get_queryset_for_user(user)
            .filter(is_read=False, is_archived=False)
            .update(is_read=True, read_at=timezone.now())
        )

    def archive(self, notification: InAppNotification) -> InAppNotification:
        notification.is_archived = True
        notification.archived_at = timezone.now()
        notification.save(update_fields=["is_archived", "archived_at"])
        return notification

    def soft_delete(self, notification: InAppNotification) -> InAppNotification:
        notification.is_deleted = True
        notification.deleted_at = timezone.now()
        notification.save(update_fields=["is_deleted", "deleted_at"])
        return notification
