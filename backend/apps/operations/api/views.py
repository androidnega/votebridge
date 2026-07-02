from rest_framework.response import Response
from rest_framework.views import APIView

from apps.operations.permissions import (
    CanAccessElectionOperations,
    CanAccessPlatformOperationsCenter,
)
from apps.operations.services.operations_service import (
    operations_activity_service,
    operations_dashboard_service,
    operations_health_service,
    operations_performance_service,
)
from apps.operations.validators import validate_activity_category
from apps.security.services.monitoring_service import monitoring_service


class OperationsOverviewView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_dashboard_service.get_overview()
        return Response({"success": True, "data": data})


class OperationsActivityView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        category = validate_activity_category(request.query_params.get("category"))
        search = request.query_params.get("search", "").strip() or None
        hours = int(request.query_params.get("hours", 24))
        limit = min(int(request.query_params.get("limit", 50)), 100)
        offset = int(request.query_params.get("offset", 0))
        data = operations_activity_service.list_activity(
            category=category,
            search=search,
            hours=hours,
            limit=limit,
            offset=offset,
        )
        return Response({"success": True, "data": data})


class OperationsHealthView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_health_service.check_all()
        return Response({"success": True, "data": data})


class OperationsInfrastructureView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_dashboard_service.get_infrastructure()
        return Response({"success": True, "data": data})


class OperationsElectionMonitorView(APIView):
    permission_classes = [CanAccessElectionOperations]

    def get(self, request):
        data = operations_dashboard_service.get_election_monitor()
        return Response({"success": True, "data": data})


class OperationsSessionsView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_dashboard_service.get_sessions_detail()
        return Response({"success": True, "data": data})


class OperationsCommunicationsView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_dashboard_service.get_communications_detail()
        return Response({"success": True, "data": data})


class OperationsQueuesView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_dashboard_service.get_queues()
        return Response({"success": True, "data": data})


class OperationsPerformanceView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        data = operations_performance_service.get_metrics()
        return Response({"success": True, "data": data})


class OperationsLogsView(APIView):
    permission_classes = [CanAccessPlatformOperationsCenter]

    def get(self, request):
        event_type = request.query_params.get("event_type")
        hours = int(request.query_params.get("hours", 24))
        limit = min(int(request.query_params.get("limit", 50)), 200)
        offset = int(request.query_params.get("offset", 0))
        search = request.query_params.get("search", "").strip() or None

        data = operations_activity_service.list_activity(
            category=None,
            search=search,
            hours=hours,
            limit=limit,
            offset=offset,
        )
        if event_type:
            data["items"] = [i for i in data["items"] if i["event_type"] == event_type]

        from apps.security.models import AuditLog

        monitoring_service.record_event(
            event_type=AuditLog.EventType.ADMIN_ACTION,
            user=request.user,
            metadata={"action": "operations_logs_viewed", "hours": hours},
        )
        return Response({"success": True, "data": data})
