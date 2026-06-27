from rest_framework import serializers


class AuditLogSerializer(serializers.Serializer):
    audit_id = serializers.UUIDField()
    event_type = serializers.CharField()
    user_email = serializers.EmailField(allow_null=True)
    user_name = serializers.CharField(allow_null=True)
    election_uuid = serializers.UUIDField(allow_null=True)
    election_title = serializers.CharField(allow_null=True)
    ip_address = serializers.CharField(allow_null=True)
    device_type = serializers.CharField(allow_null=True)
    country = serializers.CharField(allow_null=True)
    timestamp = serializers.DateTimeField()
    metadata = serializers.JSONField()


class DeviceLogSerializer(serializers.Serializer):
    device_log_id = serializers.UUIDField()
    user_email = serializers.EmailField(allow_null=True)
    user_name = serializers.CharField(allow_null=True)
    device_type = serializers.CharField()
    operating_system = serializers.CharField()
    user_agent = serializers.CharField()
    last_seen_at = serializers.DateTimeField()


class LocationLogSerializer(serializers.Serializer):
    location_log_id = serializers.UUIDField()
    ip_address = serializers.CharField()
    country = serializers.CharField()
    region = serializers.CharField()
    city = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True)
    last_seen_at = serializers.DateTimeField()


class MonitoringSummarySerializer(serializers.Serializer):
    audit = serializers.DictField()
    devices = serializers.DictField()
    locations = serializers.DictField()
    alerts = serializers.DictField()
