from django.urls import path

from apps.operations.api import views

app_name = "operations"

urlpatterns = [
    path("overview/", views.OperationsOverviewView.as_view(), name="overview"),
    path("activity/", views.OperationsActivityView.as_view(), name="activity"),
    path("health/", views.OperationsHealthView.as_view(), name="health"),
    path("infrastructure/", views.OperationsInfrastructureView.as_view(), name="infrastructure"),
    path("elections/", views.OperationsElectionMonitorView.as_view(), name="election-monitor"),
    path("sessions/", views.OperationsSessionsView.as_view(), name="sessions"),
    path("communications/", views.OperationsCommunicationsView.as_view(), name="communications"),
    path("queues/", views.OperationsQueuesView.as_view(), name="queues"),
    path("performance/", views.OperationsPerformanceView.as_view(), name="performance"),
    path("logs/", views.OperationsLogsView.as_view(), name="logs"),
]
