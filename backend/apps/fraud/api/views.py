from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.fraud.api.fraud_serializers import (
    CaseActionSerializer,
    FraudCaseSerializer,
    FraudIntegrityReportSerializer,
    InvestigationNoteSerializer,
    TimelineEventSerializer,
)
from apps.fraud.api.serializers import SecurityAlertSerializer
from apps.fraud.permissions import CanManageFraudCases, CanViewFraudCases
from apps.fraud.services.alert_service import security_alert_service
from apps.fraud.services.fraud_case_service import fraud_case_service
from apps.security.permissions import CanManageSecurityAlerts, CanViewSecurityMonitoring


def _serialize_alert(alert) -> dict:
    return {
        "alert_id": alert.alert_id,
        "alert_type": alert.alert_type,
        "status": alert.status,
        "title": alert.title,
        "description": alert.description,
        "user_email": alert.user.email if alert.user else None,
        "user_name": alert.user.get_full_name() if alert.user else None,
        "election_uuid": alert.election.uuid if alert.election else None,
        "election_title": alert.election.title if alert.election else None,
        "created_at": alert.created_at,
        "reviewed_at": alert.reviewed_at,
        "resolved_at": alert.resolved_at,
        "escalated_at": alert.escalated_at,
        "metadata": alert.metadata,
    }


class SecurityAlertListView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        status_filter = request.query_params.get("status")
        alert_type = request.query_params.get("alert_type")
        election_uuid = request.query_params.get("election_uuid")
        alerts = security_alert_service.list_alerts(
            status=status_filter,
            alert_type=alert_type,
            election_uuid=election_uuid,
        )[:200]
        data = [_serialize_alert(a) for a in alerts]
        return Response({"success": True, "data": SecurityAlertSerializer(data, many=True).data})


class SecurityAlertDetailView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request, alert_id):
        alert = security_alert_service.get_alert(alert_id)
        return Response({"success": True, "data": SecurityAlertSerializer(_serialize_alert(alert)).data})


class ReviewAlertView(APIView):
    permission_classes = [CanManageSecurityAlerts]

    def post(self, request, alert_id):
        alert = security_alert_service.review_alert(alert_id, request.user)
        return Response({"success": True, "data": SecurityAlertSerializer(_serialize_alert(alert)).data})


class ResolveAlertView(APIView):
    permission_classes = [CanManageSecurityAlerts]

    def post(self, request, alert_id):
        alert = security_alert_service.resolve_alert(alert_id, request.user)
        return Response({"success": True, "data": SecurityAlertSerializer(_serialize_alert(alert)).data})


class EscalateAlertView(APIView):
    permission_classes = [CanManageSecurityAlerts]

    def post(self, request, alert_id):
        alert = security_alert_service.escalate_alert(alert_id, request.user)
        return Response({"success": True, "data": SecurityAlertSerializer(_serialize_alert(alert)).data})


def _serialize_fraud_case(case) -> dict:
    alert = case.related_alert
    return {
        "fraud_case_id": case.fraud_case_id,
        "election_uuid": case.election.uuid if case.election else None,
        "election_title": case.election.title if case.election else None,
        "user_uuid": case.user.uuid if case.user else None,
        "user_email": case.user.email if case.user else None,
        "user_name": case.user.get_full_name() if case.user else None,
        "related_alert_id": alert.alert_id,
        "alert_type": alert.alert_type,
        "alert_title": alert.title,
        "risk_score": case.risk_score,
        "severity": case.severity,
        "status": case.status,
        "investigation_notes": case.investigation_notes,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


class FraudIntegrityReportView(APIView):
    permission_classes = [CanViewFraudCases]

    def get(self, request):
        election_uuid = request.query_params.get("election_uuid")
        report = fraud_case_service.get_integrity_report(election_uuid=election_uuid)
        return Response(
            {"success": True, "data": FraudIntegrityReportSerializer(report).data}
        )


class FraudCaseListView(APIView):
    permission_classes = [CanViewFraudCases]

    def get(self, request):
        cases = fraud_case_service.list_cases(
            status=request.query_params.get("status"),
            severity=request.query_params.get("severity"),
            election_uuid=request.query_params.get("election_uuid"),
        )[:200]
        data = [_serialize_fraud_case(c) for c in cases]
        return Response({"success": True, "data": FraudCaseSerializer(data, many=True).data})


class FraudCaseDetailView(APIView):
    permission_classes = [CanViewFraudCases]

    def get(self, request, fraud_case_id):
        case = fraud_case_service.get_case(fraud_case_id)
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})


class FraudCaseTimelineView(APIView):
    permission_classes = [CanViewFraudCases]

    def get(self, request, fraud_case_id):
        timeline = fraud_case_service.get_timeline(fraud_case_id)
        return Response(
            {"success": True, "data": TimelineEventSerializer(timeline, many=True).data}
        )


class StartInvestigationView(APIView):
    permission_classes = [CanManageFraudCases]

    def post(self, request, fraud_case_id):
        case = fraud_case_service.start_investigation(fraud_case_id, request.user)
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})


class AddInvestigationNoteView(APIView):
    permission_classes = [CanManageFraudCases]

    def post(self, request, fraud_case_id):
        serializer = InvestigationNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = fraud_case_service.add_investigation_note(
            fraud_case_id,
            request.user,
            serializer.validated_data["note"],
        )
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})


class ResolveFraudCaseView(APIView):
    permission_classes = [CanManageFraudCases]

    def post(self, request, fraud_case_id):
        serializer = CaseActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = fraud_case_service.resolve_case(
            fraud_case_id,
            request.user,
            note=serializer.validated_data.get("note", ""),
        )
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})


class DismissFraudCaseView(APIView):
    permission_classes = [CanManageFraudCases]

    def post(self, request, fraud_case_id):
        serializer = CaseActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = fraud_case_service.dismiss_case(
            fraud_case_id,
            request.user,
            note=serializer.validated_data.get("note", ""),
        )
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})


class EscalateFraudCaseView(APIView):
    permission_classes = [CanManageFraudCases]

    def post(self, request, fraud_case_id):
        serializer = CaseActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = fraud_case_service.escalate_case(
            fraud_case_id,
            request.user,
            note=serializer.validated_data.get("note", ""),
        )
        return Response({"success": True, "data": FraudCaseSerializer(_serialize_fraud_case(case)).data})
