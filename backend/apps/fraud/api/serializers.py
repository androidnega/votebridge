from rest_framework import serializers


class SecurityAlertSerializer(serializers.Serializer):
    alert_id = serializers.UUIDField()
    alert_type = serializers.CharField()
    status = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    user_email = serializers.EmailField(allow_null=True)
    user_name = serializers.CharField(allow_null=True)
    election_uuid = serializers.UUIDField(allow_null=True)
    election_title = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    reviewed_at = serializers.DateTimeField(allow_null=True)
    resolved_at = serializers.DateTimeField(allow_null=True)
    escalated_at = serializers.DateTimeField(allow_null=True)
    metadata = serializers.JSONField()
