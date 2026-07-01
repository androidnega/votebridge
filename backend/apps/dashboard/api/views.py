from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name
from apps.dashboard.services.dashboard_service import dashboard_service
from apps.fraud.permissions import CanViewFraudCases
from apps.security.permissions import CanViewSecurityMonitoring


class AdminDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = _user_role_name(request.user)
        if role not in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return Response(
                {"success": False, "error": {"message": "Admin access required.", "code": "forbidden"}},
                status=403,
            )
        return Response({"success": True, "data": dashboard_service.get_admin_overview()})


class StudentDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = _user_role_name(request.user)
        if role not in {Role.Name.STUDENT, Role.Name.CANDIDATE, Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return Response(
                {"success": False, "error": {"message": "Access denied.", "code": "forbidden"}},
                status=403,
            )
        return Response({"success": True, "data": dashboard_service.get_student_overview(request.user)})


class StudentElectionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_uuid):
        role = _user_role_name(request.user)
        if role not in {Role.Name.STUDENT, Role.Name.CANDIDATE, Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            return Response(
                {"success": False, "error": {"message": "Access denied.", "code": "forbidden"}},
                status=403,
            )

        detail = dashboard_service.get_student_election_detail(request.user, election_uuid)
        if not detail:
            return Response(
                {"success": False, "error": {"message": "Election not found.", "code": "not_found"}},
                status=404,
            )
        return Response({"success": True, "data": detail})


class SecurityFeedSnapshotView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        return Response({"success": True, "data": dashboard_service.get_security_feed_snapshot()})


class FraudFeedSnapshotView(APIView):
    permission_classes = [CanViewFraudCases]

    def get(self, request):
        return Response({"success": True, "data": dashboard_service.get_fraud_feed_snapshot()})
