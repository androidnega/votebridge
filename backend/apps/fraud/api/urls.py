from django.urls import path

from apps.fraud.api.views import (
    AddInvestigationNoteView,
    DismissFraudCaseView,
    EscalateAlertView,
    EscalateFraudCaseView,
    FraudCaseDetailView,
    FraudCaseListView,
    FraudCaseTimelineView,
    FraudIntegrityReportView,
    ResolveAlertView,
    ResolveFraudCaseView,
    ReviewAlertView,
    SecurityAlertDetailView,
    SecurityAlertListView,
    StartInvestigationView,
)

app_name = "fraud"

urlpatterns = [
    path("alerts/", SecurityAlertListView.as_view(), name="alert-list"),
    path("alerts/<uuid:alert_id>/", SecurityAlertDetailView.as_view(), name="alert-detail"),
    path("alerts/<uuid:alert_id>/review/", ReviewAlertView.as_view(), name="alert-review"),
    path("alerts/<uuid:alert_id>/resolve/", ResolveAlertView.as_view(), name="alert-resolve"),
    path("alerts/<uuid:alert_id>/escalate/", EscalateAlertView.as_view(), name="alert-escalate"),
    path("integrity-report/", FraudIntegrityReportView.as_view(), name="integrity-report"),
    path("cases/", FraudCaseListView.as_view(), name="case-list"),
    path("cases/<uuid:fraud_case_id>/", FraudCaseDetailView.as_view(), name="case-detail"),
    path("cases/<uuid:fraud_case_id>/timeline/", FraudCaseTimelineView.as_view(), name="case-timeline"),
    path("cases/<uuid:fraud_case_id>/investigate/", StartInvestigationView.as_view(), name="case-investigate"),
    path("cases/<uuid:fraud_case_id>/notes/", AddInvestigationNoteView.as_view(), name="case-add-note"),
    path("cases/<uuid:fraud_case_id>/resolve/", ResolveFraudCaseView.as_view(), name="case-resolve"),
    path("cases/<uuid:fraud_case_id>/dismiss/", DismissFraudCaseView.as_view(), name="case-dismiss"),
    path("cases/<uuid:fraud_case_id>/escalate/", EscalateFraudCaseView.as_view(), name="case-escalate"),
]
