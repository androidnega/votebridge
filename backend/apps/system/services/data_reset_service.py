"""Super-admin operational data reset — elections, votes, and results."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from apps.elections.services.election_purge_service import election_purge_service
from apps.notifications.models import DeliveryLog, InAppNotification
from apps.security.models import AuditLog
from apps.ussd.models import USSDRequestLog, USSDSession
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")

RESET_CONFIRMATION_PHRASE = "RESET OPERATIONAL DATA"


class DataResetService:
    def reset_operational_data(self, *, actor, confirmation: str) -> dict:
        if confirmation != RESET_CONFIRMATION_PHRASE:
            raise ValidationError(
                message=f'Type "{RESET_CONFIRMATION_PHRASE}" to confirm this action.',
                code="invalid_confirmation",
            )

        if settings.DEBUG is False and not getattr(settings, "ALLOW_OPERATIONAL_DATA_RESET", False):
            raise ValidationError(
                message="Operational data reset is disabled in this environment.",
                code="reset_disabled",
            )

        with transaction.atomic():
            summary = election_purge_service.reset_all_operational_data()
            notifications_removed, _ = InAppNotification.objects.filter(category="election").delete()
            delivery_logs_removed, _ = DeliveryLog.objects.filter(template_code__startswith="election").delete()
            ussd_sessions_removed, _ = USSDSession.objects.all().delete()
            ussd_logs_removed, _ = USSDRequestLog.objects.all().delete()

            cache.delete("analytics:overview")
            cache.delete("operations:overview")

            AuditLog.objects.create(
                user=actor,
                event_type=AuditLog.EventType.ADMIN_ACTION,
                metadata={
                    "action": "reset_operational_data",
                    **summary.as_dict(),
                    "notifications_removed": notifications_removed,
                    "delivery_logs_removed": delivery_logs_removed,
                    "ussd_sessions_removed": ussd_sessions_removed,
                    "ussd_logs_removed": ussd_logs_removed,
                },
            )

        logger.warning("Operational data reset by %s — %s elections removed", actor.uuid, summary.elections_removed)
        return {
            **summary.as_dict(),
            "notifications_removed": notifications_removed,
            "delivery_logs_removed": delivery_logs_removed,
            "ussd_sessions_removed": ussd_sessions_removed,
            "ussd_logs_removed": ussd_logs_removed,
        }


data_reset_service = DataResetService()
