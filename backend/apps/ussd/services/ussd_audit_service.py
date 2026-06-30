import logging

from apps.ussd.models import USSDRequestLog
from apps.ussd.repositories.ussd_repository import USSDRequestLogRepository

logger = logging.getLogger("votebridge")


class UssdAuditService:
    """Persists callback-level audit metadata alongside flow request logs."""

    def __init__(self, log_repository: USSDRequestLogRepository | None = None):
        self.log_repository = log_repository or USSDRequestLogRepository()

    def record_callback(
        self,
        *,
        session_id: str,
        msisdn: str = "",
        provider_user_id: str = "",
        request_payload: dict | None = None,
        response_payload: dict | None = None,
        http_status: int = 200,
        duration_ms: int = 0,
        ip_address: str | None = None,
    ) -> USSDRequestLog | None:
        if not session_id:
            logger.warning("USSD callback audit skipped — missing session ID.")
            return None

        audit_fields = {
            "request_payload": request_payload or {},
            "response_payload": response_payload or {},
            "http_status": http_status,
            "provider_user_id": provider_user_id,
        }
        if duration_ms:
            audit_fields["duration_ms"] = duration_ms
        if ip_address:
            audit_fields["ip_address"] = ip_address

        log = (
            self.log_repository.get_queryset()
            .filter(carrier_session_id=session_id)
            .order_by("-created_at")
            .first()
        )
        if log:
            for key, value in audit_fields.items():
                setattr(log, key, value)
            log.save(update_fields=list(audit_fields.keys()))
            return log

        outcome = (
            USSDRequestLog.Outcome.SUCCESS
            if http_status == 200
            else USSDRequestLog.Outcome.ERROR
        )
        return self.log_repository.create(
            session=None,
            carrier_session_id=session_id,
            msisdn=msisdn,
            outcome=outcome,
            continue_session=bool((response_payload or {}).get("continueSession")),
            response_message=(response_payload or {}).get("message", ""),
            **audit_fields,
        )


ussd_audit_service = UssdAuditService()
