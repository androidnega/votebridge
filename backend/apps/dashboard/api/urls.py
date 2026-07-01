from django.urls import path

from apps.dashboard.api.views import (
    AdminDashboardOverviewView,
    FraudFeedSnapshotView,
    SecurityFeedSnapshotView,
    StudentDashboardOverviewView,
    StudentElectionDetailView,
)

app_name = "dashboard"

urlpatterns = [
    path("admin/", AdminDashboardOverviewView.as_view(), name="admin-overview"),
    path("student/", StudentDashboardOverviewView.as_view(), name="student-overview"),
    path(
        "student/elections/<uuid:election_uuid>/",
        StudentElectionDetailView.as_view(),
        name="student-election-detail",
    ),
    path("security-feed/", SecurityFeedSnapshotView.as_view(), name="security-feed"),
    path("fraud-feed/", FraudFeedSnapshotView.as_view(), name="fraud-feed"),
]
