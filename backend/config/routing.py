"""
WebSocket URL routing for VoteBridge Channels.
"""

from django.urls import path

from apps.realtime import consumers as realtime_consumers

websocket_urlpatterns = [
    path("ws/realtime/dashboard/", realtime_consumers.DashboardConsumer.as_asgi()),
    path(
        "ws/realtime/elections/<uuid:election_uuid>/",
        realtime_consumers.ElectionConsumer.as_asgi(),
    ),
    path("ws/realtime/security/", realtime_consumers.SecurityConsumer.as_asgi()),
    path("ws/realtime/fraud/", realtime_consumers.FraudConsumer.as_asgi()),
    path("ws/realtime/results/", realtime_consumers.ResultsConsumer.as_asgi()),
    path("ws/realtime/strongroom/", realtime_consumers.StrongroomConsumer.as_asgi()),
    path("ws/realtime/communications/", realtime_consumers.CommunicationsConsumer.as_asgi()),
    path("ws/realtime/notifications/", realtime_consumers.NotificationConsumer.as_asgi()),
    path("ws/realtime/ussd/", realtime_consumers.UssdConsumer.as_asgi()),
    path("ws/realtime/operations/", realtime_consumers.OperationsConsumer.as_asgi()),
    path("ws/realtime/analytics/", realtime_consumers.AnalyticsConsumer.as_asgi()),
]
