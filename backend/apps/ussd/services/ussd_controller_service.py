import json
import logging
import uuid

from django.conf import settings

from apps.ussd.services.ussd_flow_service import UssdFlowService, UssdResponse, ussd_flow_service
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")


class UssdControllerService:
    """Parses Arkesel USSD callbacks and returns provider-formatted responses."""

    def __init__(self, flow_service: UssdFlowService | None = None):
        self.flow_service = flow_service or ussd_flow_service

    def handle_callback(self, request) -> tuple[str, str, dict | None]:
        """
        Returns (content_type, body, json_response_or_none).
        Supports Arkesel form-encoded (CON/END) and JSON API formats.
        """
        payload = self._parse_request(request)
        inputs = self._parse_inputs(payload)
        is_new = payload.get("new_session", payload.get("type") == "initiation" or not inputs)

        try:
            response = self.flow_service.handle_request(
                session_id=payload["session_id"],
                msisdn=payload["msisdn"],
                inputs=inputs,
                service_code=payload.get("service_code", ""),
                network=payload.get("network", ""),
                ip_address=self._client_ip(request),
                is_new_session=is_new,
            )
        except ValidationError as exc:
            message = getattr(exc, "message", str(exc))
            response = UssdResponse(f"END {message}", False)

        self._broadcast_session_update(payload["session_id"], response)

        if payload.get("format") == "json":
            json_body = {
                "sessionID": payload["session_id"],
                "userID": getattr(settings, "ARKESEL_USSD_USER_ID", "VOTEBRIDGE"),
                "msisdn": payload["msisdn"],
                "message": response.message.replace("CON ", "").replace("END ", ""),
                "continueSession": response.continue_session,
            }
            return "application/json", json.dumps(json_body), json_body

        plain = response.message
        if not plain.startswith(("CON ", "END ")):
            prefix = "CON" if response.continue_session else "END"
            plain = f"{prefix} {plain}"
        return "text/plain", plain, None

    def _parse_request(self, request) -> dict:
        content_type = request.content_type or ""
        if "application/json" in content_type:
            try:
                data = json.loads(request.body.decode("utf-8") if request.body else "{}")
            except json.JSONDecodeError:
                data = {}
            session_id = data.get("sessionID") or data.get("sessionId") or str(uuid.uuid4())
            msisdn = self._normalize_msisdn(data.get("msisdn") or data.get("phoneNumber", ""))
            user_data = data.get("userData") or data.get("text") or ""
            return {
                "format": "json",
                "session_id": session_id,
                "msisdn": msisdn,
                "raw_text": user_data,
                "service_code": data.get("userData", "") if data.get("newSession") else "",
                "network": data.get("network", ""),
                "new_session": bool(data.get("newSession")),
            }

        data = request.POST
        session_id = data.get("sessionId") or data.get("sessionID") or str(uuid.uuid4())
        msisdn = self._normalize_msisdn(data.get("phoneNumber") or data.get("msisdn", ""))
        text = data.get("text", "")
        return {
            "format": "form",
            "session_id": session_id,
            "msisdn": msisdn,
            "raw_text": text,
            "service_code": data.get("serviceCode", ""),
            "network": data.get("network", ""),
            "new_session": text == "",
            "type": data.get("type", ""),
        }

    def _parse_inputs(self, payload: dict) -> list[str]:
        raw = payload.get("raw_text", "")
        if not raw:
            return []
        if payload.get("format") == "json" and payload.get("new_session"):
            return []
        return [part.strip() for part in raw.split("*") if part.strip()]

    def _normalize_msisdn(self, msisdn: str) -> str:
        return msisdn.replace("+", "").replace(" ", "").strip()

    def _client_ip(self, request) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def _broadcast_session_update(self, session_id: str, response: UssdResponse) -> None:
        try:
            from apps.ussd.repositories.ussd_repository import USSDSessionRepository
            from core.realtime.broadcasting import realtime_broadcast_service

            session = USSDSessionRepository().get_by_session_id(session_id)
            if session:
                realtime_broadcast_service.ussd_session_updated(session, response.continue_session)
        except Exception:
            logger.debug("USSD realtime broadcast skipped")


ussd_controller_service = UssdControllerService()
