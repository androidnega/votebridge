from rest_framework import serializers


class BiometricEnrollmentSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField()
    images = serializers.ListField(
        child=serializers.CharField(),
        min_length=10,
        max_length=15,
    )


class BiometricVerifyLoginSerializer(serializers.Serializer):
    pending_auth_token = serializers.CharField()
    challenge_id = serializers.CharField()
    frames = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        max_length=30,
    )
    device_signals = serializers.DictField(required=False)


class BiometricStepUpSerializer(serializers.Serializer):
    challenge_id = serializers.CharField()
    frames = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        max_length=30,
    )
    action = serializers.CharField(max_length=64)


class BiometricChallengeRequestSerializer(serializers.Serializer):
    pending_auth_token = serializers.CharField(required=False, allow_blank=True)


class BiometricStatusSerializer(serializers.Serializer):
    module_enabled = serializers.BooleanField()
    required_for_user = serializers.BooleanField()
    enrolled = serializers.BooleanField()
    is_locked = serializers.BooleanField()
    last_verified_at = serializers.DateTimeField(allow_null=True)
    quality_score = serializers.FloatField(allow_null=True)
    model_version = serializers.CharField(allow_null=True)
    failed_attempts = serializers.IntegerField()


class BiometricHistorySerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    event_type = serializers.CharField()
    outcome = serializers.CharField()
    challenge_type = serializers.CharField()
    confidence = serializers.FloatField(allow_null=True)
    liveness_score = serializers.FloatField(allow_null=True)
    processing_time_ms = serializers.IntegerField(allow_null=True)
    model_version = serializers.CharField()
    ip_address = serializers.IPAddressField(allow_null=True)
    created_at = serializers.DateTimeField()
