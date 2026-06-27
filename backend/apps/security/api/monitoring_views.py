from rest_framework.response import Response
from rest_framework.views import APIView

from apps.fraud.api.serializers import SecurityAlertSerializer
from apps.fraud.services.alert_service import security_alert_service
from apps.security.permissions import CanManageSecurityAlerts, CanViewSecurityMonitoring


class SecurityCenterSummaryView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        from apps.fraud.services.alert_service import (
            audit_log_service,
            device_monitoring_service,
            location_monitoring_service,
        )

        return Response(
            {
                "success": True,
                "data": {
                    "audit": audit_log_service.get_summary(),
                    "devices": device_monitoring_service.get_summary(),
                    "locations": location_monitoring_service.get_summary(),
                    "alerts": security_alert_service.get_summary(),
                },
            }
        )


class AuditLogListView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        from apps.fraud.services.alert_service import audit_log_service

        event_type = request.query_params.get("event_type")
        election_uuid = request.query_params.get("election_uuid")
        hours = request.query_params.get("hours")
        logs = audit_log_service.list_logs(
            event_type=event_type,
            election_uuid=election_uuid,
            hours=int(hours) if hours else 24,
        )
        data = [
            {
                "audit_id": log.audit_id,
                "event_type": log.event_type,
                "user_email": log.user.email if log.user else None,
                "user_name": log.user.get_full_name() if log.user else None,
                "election_uuid": log.election.uuid if log.election else None,
                "election_title": log.election.title if log.election else None,
                "ip_address": log.ip_address,
                "device_type": log.device_log.device_type if log.device_log else None,
                "country": log.location_log.country if log.location_log else None,
                "timestamp": log.timestamp,
                "metadata": log.metadata,
            }
            for log in logs[:200]
        ]
        from apps.security.api.monitoring_serializers import AuditLogSerializer

        return Response({"success": True, "data": AuditLogSerializer(data, many=True).data})


class DeviceLogListView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        from apps.fraud.services.alert_service import device_monitoring_service

        device_type = request.query_params.get("device_type")
        devices = device_monitoring_service.list_devices(device_type=device_type)[:200]
        data = [
            {
                "device_log_id": d.device_log_id,
                "user_email": d.user.email if d.user else None,
                "user_name": d.user.get_full_name() if d.user else None,
                "device_type": d.device_type,
                "operating_system": d.operating_system,
                "user_agent": d.user_agent[:200],
                "last_seen_at": d.last_seen_at,
            }
            for d in devices
        ]
        from apps.security.api.monitoring_serializers import DeviceLogSerializer

        return Response({"success": True, "data": DeviceLogSerializer(data, many=True).data})


class LocationLogListView(APIView):
    permission_classes = [CanViewSecurityMonitoring]

    def get(self, request):
        from apps.fraud.services.alert_service import location_monitoring_service

        country = request.query_params.get("country")
        locations = location_monitoring_service.list_locations(country=country)[:200]
        data = [
            {
                "location_log_id": loc.location_log_id,
                "ip_address": loc.ip_address,
                "country": loc.country,
                "region": loc.region,
                "city": loc.city,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "last_seen_at": loc.last_seen_at,
            }
            for loc in locations
        ]
        from apps.security.api.monitoring_serializers import LocationLogSerializer

        return Response({"success": True, "data": LocationLogSerializer(data, many=True).data})
