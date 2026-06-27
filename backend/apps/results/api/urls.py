from django.urls import path

from apps.results.api import views

app_name = "results"

urlpatterns = [
    path("elections/", views.ElectionResultListView.as_view(), name="result-list"),
    path("certification-queue/", views.CertificationQueueView.as_view(), name="certification-queue"),
    path("publication-queue/", views.PublicationQueueView.as_view(), name="publication-queue"),
    path("archive-queue/", views.ArchiveQueueView.as_view(), name="archive-queue"),
    path("elections/<uuid:election_uuid>/", views.ElectionResultDetailView.as_view(), name="result-detail"),
    path("elections/<uuid:election_uuid>/generate/", views.GenerateResultsView.as_view(), name="result-generate"),
    path("elections/<uuid:election_uuid>/preview/", views.PreviewResultsView.as_view(), name="result-preview"),
    path("elections/<uuid:election_uuid>/integrity/", views.IntegrityReportView.as_view(), name="result-integrity"),
    path("elections/<uuid:election_uuid>/certify/", views.CertifyResultsView.as_view(), name="result-certify"),
    path("elections/<uuid:election_uuid>/publish/", views.PublishResultsView.as_view(), name="result-publish"),
    path("elections/<uuid:election_uuid>/archive/", views.ArchiveResultsView.as_view(), name="result-archive"),
    path(
        "elections/<uuid:election_uuid>/reports/<str:report_format>/",
        views.ResultReportView.as_view(),
        name="result-report",
    ),
]
