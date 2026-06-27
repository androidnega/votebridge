from django.urls import path

from apps.strongroom.api import views

app_name = "strongroom"

urlpatterns = [
    path("elections/", views.StrongroomListView.as_view(), name="strongroom-list"),
    path(
        "elections/<uuid:election_uuid>/dashboard/",
        views.StrongroomDashboardView.as_view(),
        name="strongroom-dashboard",
    ),
    path(
        "elections/<uuid:election_uuid>/custody/",
        views.CustodyTimelineView.as_view(),
        name="custody-timeline",
    ),
    path(
        "elections/<uuid:election_uuid>/verify/",
        views.VerifyIntegrityView.as_view(),
        name="verify-integrity",
    ),
    path(
        "elections/<uuid:election_uuid>/lock/",
        views.LockElectionView.as_view(),
        name="lock-election",
    ),
    path("public/verify/", views.PublicVerificationView.as_view(), name="public-verify"),
]
