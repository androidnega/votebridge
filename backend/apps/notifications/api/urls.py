from django.urls import path

from apps.notifications.api import views

app_name = "notifications"

urlpatterns = [
    path("dashboard/", views.CommunicationDashboardView.as_view(), name="dashboard"),
    path("deliveries/", views.DeliveryLogListView.as_view(), name="delivery-list"),
    path("deliveries/<uuid:log_uuid>/retry/", views.DeliveryRetryView.as_view(), name="delivery-retry"),
    path("queue/process/", views.QueueProcessView.as_view(), name="queue-process"),
    path("templates/", views.TemplateListView.as_view(), name="template-list"),
    path("providers/", views.ProviderListView.as_view(), name="provider-list"),
    path("providers/<uuid:provider_uuid>/test/", views.ProviderTestView.as_view(), name="provider-test"),
    path("test/", views.TestMessageView.as_view(), name="test-message"),
    path("center/", views.NotificationCenterView.as_view(), name="notification-center"),
    path("center/read-all/", views.NotificationMarkAllReadView.as_view(), name="notification-read-all"),
    path("center/<uuid:notification_uuid>/read/", views.NotificationMarkReadView.as_view(), name="notification-read"),
    path(
        "center/<uuid:notification_uuid>/archive/",
        views.NotificationArchiveView.as_view(),
        name="notification-archive",
    ),
    path(
        "center/<uuid:notification_uuid>/",
        views.NotificationDeleteView.as_view(),
        name="notification-delete",
    ),
]
