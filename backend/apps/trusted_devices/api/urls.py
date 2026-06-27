from django.urls import path

from apps.trusted_devices.api import views

app_name = "trusted_devices"

urlpatterns = [
    path("", views.TrustedDeviceListView.as_view(), name="list"),
    path("current/", views.TrustedDeviceCurrentView.as_view(), name="current"),
    path("policy/", views.TrustedDevicePolicyView.as_view(), name="policy"),
    path("session-status/", views.TrustedDeviceSessionStatusView.as_view(), name="session-status"),
    path("reverify/", views.TrustedDeviceForceReverifyView.as_view(), name="reverify"),
    path("<uuid:device_uuid>/history/", views.TrustedDeviceHistoryView.as_view(), name="history"),
    path("<uuid:device_uuid>/rename/", views.TrustedDeviceRenameView.as_view(), name="rename"),
    path("<uuid:device_uuid>/revoke/", views.TrustedDeviceRevokeView.as_view(), name="revoke"),
    path("<uuid:device_uuid>/assign-university/", views.TrustedDeviceAssignUniversityView.as_view(), name="assign-university"),
    path("<uuid:device_uuid>/", views.TrustedDeviceDeleteView.as_view(), name="delete"),
]
