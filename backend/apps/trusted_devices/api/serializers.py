from rest_framework import serializers


class DeviceRenameSerializer(serializers.Serializer):
    device_name = serializers.CharField(max_length=128)


class DeviceRevokeSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField(required=False)


class TrustedDeviceSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    device_name = serializers.CharField()
    browser_name = serializers.CharField()
    browser_version = serializers.CharField()
    operating_system = serializers.CharField()
    platform = serializers.CharField()
    last_country = serializers.CharField()
    last_city = serializers.CharField()
    last_ip = serializers.IPAddressField(allow_null=True)
    last_seen = serializers.DateTimeField()
    last_verified = serializers.DateTimeField(allow_null=True)
    last_biometric = serializers.DateTimeField(allow_null=True)
    is_trusted = serializers.BooleanField()
    is_revoked = serializers.BooleanField()
    expires_at = serializers.DateTimeField()
    risk_score = serializers.FloatField()
    is_current = serializers.BooleanField(required=False)
