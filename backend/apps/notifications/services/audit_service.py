import logging

from apps.security.services.monitoring_service import monitoring_service

logger = logging.getLogger("votebridge")


class CommunicationAuditService:
    """Writes communication actions to the system audit log."""

    def record(self, actor=None, log=None, provider=None, action: str = "", extra: dict | None = None):
        metadata = {"communication_action": action, **(extra or {})}
        if log:
            metadata.update(
                {
                    "delivery_uuid": str(log.uuid),
                    "channel": log.channel,
                    "recipient": log.recipient,
                    "status": log.status,
                    "template_code": log.template_code,
                }
            )
        if provider:
            metadata["provider_uuid"] = str(provider.uuid)
            metadata["provider_type"] = provider.provider_type

        monitoring_service.record_event(
            event_type="admin_action",
            user=actor,
            metadata={
                "subsystem": "communication",
                **metadata,
            },
        )


communication_audit_service = CommunicationAuditService()
