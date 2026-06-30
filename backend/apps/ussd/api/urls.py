from django.urls import path

from apps.ussd.api import views

app_name = "ussd"

urlpatterns = [
    path("callback/", views.UssdCallbackView.as_view(), name="callback"),
    path("integration/", views.UssdIntegrationView.as_view(), name="integration"),
    path("dashboard/", views.UssdDashboardView.as_view(), name="dashboard"),
    path("sessions/", views.UssdSessionListView.as_view(), name="session-list"),
    path("sessions/<uuid:session_uuid>/", views.UssdSessionDetailView.as_view(), name="session-detail"),
    path("logs/", views.UssdRequestLogListView.as_view(), name="log-list"),
]
