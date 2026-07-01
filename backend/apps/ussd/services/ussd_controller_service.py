import json
import logging
import uuid
from urllib.parse import parse_qs

from django.conf import settings

from apps.ussd.services.ussd_flow_service import UssdFlowService, UssdResponse, ussd_flow_service
from apps.system.services.feature_flag_service import feature_flag_service
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")

USSD_DISABLED_MESSAGE = (
    "USSD voting is currently unavailable.\nPlease contact the Election Office."
)

ARKESSEL_RESPONSE_KEYS = ("sessionID", "userID", "msisdn", "message", "continueSession")


class UssdControllerService:
    """Parses Arkesel USSD callbacks and returns provider-formatted responses."""

    def __init__(self, flow_service: UssdFlowService | None = None):
        self.flow_service = flow_service or ussd_flow_service

    def handle_callback(self, request) -> tuple[str, str, dict, dict]:
        """
        Returns (content_type, body, json_response, audit_context).
        Arkesel gateway expects application/json with sessionID, userID, msisdn,
        message, and continueSession for every callback response.
        """
        payload = self._parse_request(request)
        audit_context = self._build_audit_context(request, payload)
        inputs = self._parse_inputs(payload)
        is_new = payload.get("new_session", payload.get("type") == "initiation" or not inputs)

        if not feature_flag_service.is_ussd_enabled():
            response = UssdResponse(f"END {USSD_DISABLED_MESSAGE}", False)
            json_body = self._build_arkesel_response(payload, response)
            return "application/json", json.dumps(json_body), json_body, audit_context

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

        json_body = self._build_arkesel_response(payload, response)
        if not self._validate_arkesel_response(json_body):
            logger.error("USSD callback response failed validation: %s", json_body)
            json_body = self._build_arkesel_response(
                payload,
                UssdResponse("END System error. Please try again later.", False),
            )

        return "application/json", json.dumps(json_body), json_body, audit_context

    def build_failure_response(self, request) -> tuple[str, str, dict, dict]:
        """Fallback Arkesel response when callback processing fails unexpectedly."""
        try:
            payload = self._parse_request(request)
            audit_context = self._build_audit_context(request, payload)
        except Exception:
            payload = {
                "session_id": str(uuid.uuid4()),
                "msisdn": "",
                "user_id": "",
                "format": "unknown",
            }
            audit_context = {
                "session_id": payload["session_id"],
                "msisdn": "",
                "provider_user_id": "",
                "request_payload": {},
                "ip_address": self._client_ip(request),
            }

        json_body = self._build_arkesel_response(
            payload,
            UssdResponse("END System error. Please try again later.", False),
        )
        return "application/json", json.dumps(json_body), json_body, audit_context

    def _build_arkesel_response(self, payload: dict, response: UssdResponse) -> dict:
        message = response.message
        if message.startswith("CON "):
            message = message[4:]
        elif message.startswith("END "):
            message = message[4:]

        return {
            "sessionID": payload["session_id"],
            "userID": getattr(settings, "ARKESEL_USSD_USER_ID", "VOTEBRIDGE"),
            "msisdn": payload["msisdn"],
            "message": message,
            "continueSession": response.continue_session,
        }

    def _validate_arkesel_response(self, body: dict) -> bool:
        if not isinstance(body, dict):
            return False
        for key in ARKESSEL_RESPONSE_KEYS:
            if key not in body:
                return False
        if not isinstance(body["message"], str):
            return False
        if not isinstance(body["continueSession"], bool):
            return False
        return True

    def _build_audit_context(self, request, payload: dict) -> dict:
        return {
            "session_id": payload.get("session_id", ""),
            "msisdn": payload.get("msisdn", ""),
            "provider_user_id": payload.get("user_id", ""),
            "request_payload": self._capture_request_payload(request, payload),
            "ip_address": self._client_ip(request),
        }

    def _capture_request_payload(self, request, payload: dict) -> dict:
        raw: dict = {}
        content_type = request.content_type or ""
        if "application/json" in content_type:
            try:
                raw = json.loads(request.body.decode("utf-8") if request.body else "{}")
            except json.JSONDecodeError:
                raw = {}
        else:
            raw = dict(self._form_data(request))
        return {
            "parsed": payload,
            "raw": raw,
            "content_type": content_type,
        }

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
                "user_id": data.get("userID") or data.get("userId") or "",
                "raw_text": user_data,
                "service_code": data.get("userData", "") if data.get("newSession") else "",
                "network": data.get("network", ""),
                "new_session": bool(data.get("newSession")),
            }

        data = self._form_data(request)
        session_id = data.get("sessionId") or data.get("sessionID") or str(uuid.uuid4())
        msisdn = self._normalize_msisdn(data.get("phoneNumber") or data.get("msisdn", ""))
        text = data.get("text", "")
        return {
            "format": "form",
            "session_id": session_id,
            "msisdn": msisdn,
            "user_id": data.get("userID") or data.get("userId") or "",
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

    def _form_data(self, request) -> dict:
        raw = getattr(request, "data", None)
        if raw:
            if hasattr(raw, "get"):
                return {key: raw.get(key) for key in raw.keys()}
            if hasattr(raw, "dict"):
                return raw.dict()
            return dict(raw)
        if request.POST:
            return request.POST

        content_type = request.content_type or ""
        if "application/x-www-form-urlencoded" in content_type and request.body:
            parsed = parse_qs(request.body.decode("utf-8"), keep_blank_values=True)
            return {
                key: values[0] if len(values) == 1 else values
                for key, values in parsed.items()
            }
        return {}

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
