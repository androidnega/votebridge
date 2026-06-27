from rest_framework import serializers


class OperationsOverviewSerializer(serializers.Serializer):
    pass


class ActivityItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    event_type = serializers.CharField()
    category = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    user_email = serializers.CharField(allow_null=True)
    election_title = serializers.CharField(allow_null=True)
    timestamp = serializers.DateTimeField()


class HealthComponentSerializer(serializers.Serializer):
    name = serializers.CharField()
    status = serializers.CharField()
    checked_at = serializers.CharField()
    response_time_ms = serializers.FloatField(required=False, allow_null=True)
    details = serializers.CharField(required=False, allow_blank=True)
