from django.urls import path

from apps.analytics.api import views

app_name = "analytics"

urlpatterns = [
    path("overview/", views.AnalyticsOverviewView.as_view(), name="overview"),
    path("elections/", views.AnalyticsElectionsView.as_view(), name="elections"),
    path("elections/<uuid:election_uuid>/", views.AnalyticsElectionDetailView.as_view(), name="election-detail"),
    path(
        "elections/<uuid:election_uuid>/live-trend/",
        views.AnalyticsElectionLiveTrendView.as_view(),
        name="election-live-trend",
    ),
    path(
        "elections/<uuid:election_uuid>/results-analytics/",
        views.AnalyticsElectionResultsAnalyticsView.as_view(),
        name="election-results-analytics",
    ),
    path("participation/", views.AnalyticsParticipationView.as_view(), name="participation"),
    path("departments/", views.AnalyticsDepartmentsView.as_view(), name="departments"),
    path("faculties/", views.AnalyticsFacultiesView.as_view(), name="faculties"),
    path("programmes/", views.AnalyticsProgrammesView.as_view(), name="programmes"),
    path("students/", views.AnalyticsStudentsView.as_view(), name="students"),
    path("personal/", views.AnalyticsPersonalView.as_view(), name="personal"),
    path("security/", views.AnalyticsSecurityView.as_view(), name="security"),
    path("fraud/", views.AnalyticsFraudView.as_view(), name="fraud"),
    path("operations/", views.AnalyticsOperationsView.as_view(), name="operations"),
    path("communications/", views.AnalyticsCommunicationsView.as_view(), name="communications"),
    path("ussd/", views.AnalyticsUssdView.as_view(), name="ussd"),
    path("strongroom/", views.AnalyticsStrongroomView.as_view(), name="strongroom"),
    path("historical/", views.AnalyticsHistoricalView.as_view(), name="historical"),
    path("reports/<str:report_type>/", views.AnalyticsReportView.as_view(), name="reports"),
]
