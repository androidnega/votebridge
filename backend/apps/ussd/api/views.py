import logging
import time

from django.http import HttpResponse
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.elections.permissions import CanManageVotingChannels
from apps.ussd.permissions import CanViewUssdMonitoring, UssdCallbackPermission
from apps.ussd.repositories.ussd_repository import USSDRequestLogRepository, USSDSessionRepository
from apps.ussd.services.ussd_audit_service import ussd_audit_service
from apps.ussd.services.ussd_config_service import ussd_config_service
from apps.ussd.services.ussd_controller_service import ussd_controller_service
from core.exceptions import NotFoundError

logger = logging.getLogger("votebridge")


def _serialize_session(session) -> dict:
    return {
        "uuid": str(session.uuid),
        "session_id": session.session_id,
        "msisdn": session.msisdn,
        "status": session.status,
        "current_step": session.current_step,
        "request_count": session.request_count,
        "completed_vote": session.completed_vote,
        "user_index": session.user.index_number if session.user else None,
        "started_at": session.started_at,
        "last_activity_at": session.last_activity_at,
        "ended_at": session.ended_at,
        "failure_reason": session.failure_reason,
    }


def _serialize_log(log) -> dict:
    return {
        "uuid": str(log.uuid),
        "carrier_session_id": log.carrier_session_id,
        "msisdn": log.msisdn,
        "step_before": log.step_before,
        "step_after": log.step_after,
        "outcome": log.outcome,
        "continue_session": log.continue_session,
        "duration_ms": log.duration_ms,
        "http_status": log.http_status,
        "provider_user_id": log.provider_user_id,
        "raw_input": log.raw_input,
        "response_message": log.response_message[:200] if log.response_message else "",
        "created_at": log.created_at,
    }


class UssdCallbackView(APIView):
    """Arkesel USSD webhook — form POST or JSON."""

    permission_classes = [UssdCallbackPermission]
    authentication_classes = []
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        started = time.monotonic()
        http_status = 200
        body = ""
        response_payload: dict = {}
        audit_context: dict = {}

        try:
            _content_type, body, response_payload, audit_context = (
                ussd_controller_service.handle_callback(request)
            )
        except Exception:
            logger.exception("USSD callback processing failed.")
            _content_type, body, response_payload, audit_context = (
                ussd_controller_service.build_failure_response(request)
            )
        finally:
            duration_ms = int((time.monotonic() - started) * 1000)
            ussd_audit_service.record_callback(
                session_id=audit_context.get("session_id", ""),
                msisdn=audit_context.get("msisdn", ""),
                provider_user_id=audit_context.get("provider_user_id", ""),
                request_payload=audit_context.get("request_payload", {}),
                response_payload=response_payload,
                http_status=http_status,
                duration_ms=duration_ms,
                ip_address=audit_context.get("ip_address"),
            )

        return HttpResponse(body, content_type="application/json", status=http_status)

    def get(self, request):
        return Response(
            {"success": True, "data": {"status": "VoteBridge USSD endpoint ready."}},
            content_type="application/json",
        )


class UssdIntegrationView(APIView):
    """Operational USSD callback configuration and health."""

    permission_classes = [CanManageVotingChannels]

    def get(self, request):
        return Response({"success": True, "data": ussd_config_service.get_integration_config()})


class UssdDashboardView(APIView):
    permission_classes = [CanViewUssdMonitoring]

    def get(self, request):
        repo = USSDSessionRepository()
        stats = repo.dashboard_stats()
        from apps.notifications.models import CommunicationProvider

        sms = CommunicationProvider.objects.filter(provider_type="arkesel_sms").first()
        stats["provider_status"] = sms.connection_status if sms else "unknown"
        stats["sms_sent"] = stats.get("successful_requests", 0)
        integration = ussd_config_service.get_integration_config()
        stats["callback_url"] = integration["callback_url"]
        stats["callback_path"] = integration["callback_path"]
        stats["environment"] = integration["environment"]
        stats["health_status"] = integration["health_status"]
        stats["health"] = integration["health"]
        return Response({"success": True, "data": stats})


class UssdSessionListView(APIView):
    permission_classes = [CanViewUssdMonitoring]

    def get(self, request):
        status = request.query_params.get("status")
        search = request.query_params.get("search", "").strip() or None
        limit = min(int(request.query_params.get("limit", 50)), 100)
        offset = int(request.query_params.get("offset", 0))
        repo = USSDSessionRepository()
        items, total = repo.list_filtered(status=status, search=search, limit=limit, offset=offset)
        return Response(
            {
                "success": True,
                "data": {
                    "items": [_serialize_session(s) for s in items],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                },
            }
        )


class UssdRequestLogListView(APIView):
    permission_classes = [CanViewUssdMonitoring]

    def get(self, request):
        outcome = request.query_params.get("outcome")
        search = request.query_params.get("search", "").strip() or None
        limit = min(int(request.query_params.get("limit", 50)), 100)
        offset = int(request.query_params.get("offset", 0))
        repo = USSDRequestLogRepository()
        items, total = repo.list_filtered(outcome=outcome, search=search, limit=limit, offset=offset)
        return Response(
            {
                "success": True,
                "data": {
                    "items": [_serialize_log(log) for log in items],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                },
            }
        )


class UssdSessionDetailView(APIView):
    permission_classes = [CanViewUssdMonitoring]

    def get(self, request, session_uuid):
        from apps.ussd.models import USSDSession

        session = USSDSession.objects.filter(uuid=session_uuid).select_related("user").first()
        if not session:
            raise NotFoundError(message="Session not found.", code="not_found")
        logs = session.request_logs.all()[:50]
        return Response(
            {
                "success": True,
                "data": {
                    "session": _serialize_session(session),
                    "logs": [_serialize_log(log) for log in logs],
                },
            }
        )
