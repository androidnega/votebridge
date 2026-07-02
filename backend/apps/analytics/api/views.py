from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.api.helpers import attach_candidate_image_urls
from apps.analytics.permissions import CanAccessAnalytics, CanAccessPersonalAnalytics
from apps.analytics.services.analytics_service import (
    analytics_communication_service,
    analytics_dashboard_service,
    analytics_election_service,
    analytics_fraud_service,
    analytics_historical_service,
    analytics_operations_service,
    analytics_participation_service,
    analytics_report_service,
    analytics_security_service,
    analytics_strongroom_service,
    analytics_student_service,
    analytics_ussd_service,
)
from apps.analytics.services.election_live_trend_service import election_live_trend_service
from apps.analytics.services.election_results_analytics_service import (
    election_results_analytics_service,
)
from apps.analytics.validators import validate_export_format, validate_period, validate_report_type


class AnalyticsOverviewView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_dashboard_service.get_overview()})


class AnalyticsElectionsView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_election_service.compare_elections()})


class AnalyticsElectionDetailView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request, election_uuid):
        return Response({"success": True, "data": analytics_election_service.get_election(election_uuid)})


class AnalyticsElectionLiveTrendView(APIView):
    """Internal live standings for open/paused elections — admin and super-admin only."""

    permission_classes = [CanAccessAnalytics]

    def get(self, request, election_uuid):
        data = election_live_trend_service.get_live_trend(election_uuid)
        return Response(
            {"success": True, "data": attach_candidate_image_urls(data, request)},
        )


class AnalyticsElectionResultsAnalyticsView(APIView):
    """Rich analytics for closed/archived elections — admin and super-admin only."""

    permission_classes = [CanAccessAnalytics]

    def get(self, request, election_uuid):
        data = election_results_analytics_service.get_results_analytics(election_uuid)
        return Response(
            {"success": True, "data": attach_candidate_image_urls(data, request)},
        )


class AnalyticsParticipationView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_participation_service.get_participation()})


class AnalyticsDepartmentsView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_participation_service.get_departments()})


class AnalyticsFacultiesView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_participation_service.get_faculties()})


class AnalyticsProgrammesView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_participation_service.get_programmes()})


class AnalyticsStudentsView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_student_service.get_student_analytics()})


class AnalyticsPersonalView(APIView):
    permission_classes = [CanAccessPersonalAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_student_service.get_personal_analytics(request.user)})


class AnalyticsSecurityView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_security_service.get_security_analytics()})


class AnalyticsFraudView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_fraud_service.get_fraud_analytics()})


class AnalyticsOperationsView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_operations_service.get_operations_analytics()})


class AnalyticsCommunicationsView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_communication_service.get_communication_analytics()})


class AnalyticsUssdView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_ussd_service.get_ussd_analytics()})


class AnalyticsStrongroomView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        return Response({"success": True, "data": analytics_strongroom_service.get_strongroom_analytics()})


class AnalyticsHistoricalView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request):
        period = validate_period(request.query_params.get("period"))
        return Response({"success": True, "data": analytics_historical_service.get_trends(period)})


class AnalyticsReportView(APIView):
    permission_classes = [CanAccessAnalytics]

    def get(self, request, report_type):
        report_type = validate_report_type(report_type)
        export_format = validate_export_format(request.query_params.get("format"))
        election_uuid = request.query_params.get("election_uuid")
        data = analytics_report_service.generate(
            report_type,
            export_format,
            election_uuid=election_uuid,
        )
        return Response({"success": True, "data": data})
