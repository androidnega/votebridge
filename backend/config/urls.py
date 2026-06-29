"""
URL configuration for VoteBridge.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.dashboard.views import dashboard_index, login_page
from apps.elections.views import (
    candidate_create_page,
    candidate_edit_page,
    candidate_list_page,
    election_create_page,
    election_detail_page,
    election_edit_page,
    election_list_page,
    eligibility_list_page,
    eligibility_manage_page,
    position_create_page,
    position_edit_page,
    position_list_page,
)
from apps.fraud.views import (
    fraud_case_detail_page,
    fraud_case_list_page,
    fraud_dashboard_page,
    fraud_timeline_page,
)
from apps.security.views import (
    audit_logs_page,
    device_monitoring_page,
    location_monitoring_page,
    security_alerts_page,
    security_center_page,
    svt_admin_list_page,
    svt_request_page,
    svt_verify_page,
)
from apps.voting.views import ballot_confirmation_page, ballot_page, my_votes_page


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok", "service": "votebridge"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("", dashboard_index, name="dashboard-index"),
    path("auth/login/", login_page, name="auth-login"),
    # DEPRECATED (v1.0): Legacy Django dashboard pages — use Vue SPA routes instead.
    # See docs/DEPRECATED.md. Block at Nginx in production if not required.
    path("dashboard/elections/", election_list_page, name="election-list-page"),
    path("dashboard/elections/create/", election_create_page, name="election-create-page"),
    path("dashboard/elections/<uuid:uuid>/", election_detail_page, name="election-detail-page"),
    path("dashboard/elections/<uuid:uuid>/edit/", election_edit_page, name="election-edit-page"),
    path(
        "dashboard/elections/<uuid:election_uuid>/candidates/",
        candidate_list_page,
        name="candidate-list-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/candidates/create/",
        candidate_create_page,
        name="candidate-create-page",
    ),
    path(
        "dashboard/candidates/<uuid:uuid>/edit/",
        candidate_edit_page,
        name="candidate-edit-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/positions/",
        position_list_page,
        name="position-list-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/positions/create/",
        position_create_page,
        name="position-create-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/positions/<uuid:uuid>/edit/",
        position_edit_page,
        name="position-edit-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/eligibility/",
        eligibility_list_page,
        name="eligibility-list-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/eligibility/manage/",
        eligibility_manage_page,
        name="eligibility-manage-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/svt/",
        svt_request_page,
        name="svt-request-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/svt/manage/",
        svt_admin_list_page,
        name="svt-admin-list-page",
    ),
    path(
        "dashboard/svt/verify/",
        svt_verify_page,
        name="svt-verify-page",
    ),
    path("dashboard/security/", security_center_page, name="security-center-page"),
    path("dashboard/security/audit/", audit_logs_page, name="audit-logs-page"),
    path("dashboard/security/devices/", device_monitoring_page, name="device-monitoring-page"),
    path("dashboard/security/locations/", location_monitoring_page, name="location-monitoring-page"),
    path("dashboard/security/alerts/", security_alerts_page, name="security-alerts-page"),
    path("dashboard/fraud/", fraud_dashboard_page, name="fraud-dashboard-page"),
    path("dashboard/fraud/cases/", fraud_case_list_page, name="fraud-case-list-page"),
    path("dashboard/fraud/cases/<uuid:fraud_case_id>/", fraud_case_detail_page, name="fraud-case-detail-page"),
    path("dashboard/fraud/cases/<uuid:fraud_case_id>/timeline/", fraud_timeline_page, name="fraud-timeline-page"),
    path(
        "dashboard/elections/<uuid:election_uuid>/vote/",
        ballot_page,
        name="ballot-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/vote/confirmation/",
        ballot_confirmation_page,
        name="ballot-confirmation-page",
    ),
    path(
        "dashboard/elections/<uuid:election_uuid>/my-votes/",
        my_votes_page,
        name="my-votes-page",
    ),
    path("api/v1/accounts/", include("apps.accounts.api.urls")),
    path("api/v1/elections/", include("apps.elections.api.urls")),
    path("api/v1/candidates/", include("apps.candidates.api.urls")),
    path("api/v1/voting/", include("apps.voting.api.urls")),
    path("api/v1/security/", include("apps.security.api.urls")),
    path("api/v1/fraud/", include("apps.fraud.api.urls")),
    path("api/v1/results/", include("apps.results.api.urls")),
    path("api/v1/strongroom/", include("apps.strongroom.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
    path("api/v1/ussd/", include("apps.ussd.api.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.api.urls")),
    path("api/v1/operations/", include("apps.operations.api.urls")),
    path("api/v1/system/", include("apps.system.api.urls")),
    path("api/v1/analytics/", include("apps.analytics.api.urls")),
    path("api/v1/biometrics/", include("apps.biometrics.api.urls")),
    path("api/v1/trusted-devices/", include("apps.trusted_devices.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="api-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
    except ImportError:
        pass
