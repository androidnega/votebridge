from django.urls import path

from apps.security.api.monitoring_views import (
    AuditLogListView,
    DeviceLogListView,
    LocationLogListView,
    SecurityCenterSummaryView,
)
from apps.security.api.views import (
    ElectionSVTListView,
    ReissueSVTView,
    RequestSVTView,
    ResendSVTView,
    RevokeSVTView,
    StartVotingSessionView,
    SVTConfirmationView,
    ValidateSVTView,
    VerifyVoteBySVTView,
    VotingAccessStatusView,
)

app_name = "security"

urlpatterns = [
    path(
        "elections/<uuid:election_uuid>/svt/resend/",
        ResendSVTView.as_view(),
        name="svt-resend",
    ),
    path(
        "elections/<uuid:election_uuid>/svt/access/",
        VotingAccessStatusView.as_view(),
        name="svt-access",
    ),
    path(
        "elections/<uuid:election_uuid>/svt/validate/",
        ValidateSVTView.as_view(),
        name="svt-validate",
    ),
    path(
        "elections/<uuid:election_uuid>/svt/start/",
        StartVotingSessionView.as_view(),
        name="svt-start",
    ),
    path(
        "elections/<uuid:election_uuid>/svt/request/",
        RequestSVTView.as_view(),
        name="svt-request",
    ),
    path(
        "elections/<uuid:election_uuid>/svt/",
        ElectionSVTListView.as_view(),
        name="svt-list",
    ),
    path(
        "svt/verify/",
        VerifyVoteBySVTView.as_view(),
        name="svt-verify",
    ),
    path(
        "svt/confirmation/",
        SVTConfirmationView.as_view(),
        name="svt-confirmation",
    ),
    path(
        "svt/<uuid:svt_id>/revoke/",
        RevokeSVTView.as_view(),
        name="svt-revoke",
    ),
    path(
        "svt/<uuid:svt_id>/reissue/",
        ReissueSVTView.as_view(),
        name="svt-reissue",
    ),
    path("monitoring/summary/", SecurityCenterSummaryView.as_view(), name="monitoring-summary"),
    path("monitoring/audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("monitoring/devices/", DeviceLogListView.as_view(), name="device-log-list"),
    path("monitoring/locations/", LocationLogListView.as_view(), name="location-log-list"),
]
