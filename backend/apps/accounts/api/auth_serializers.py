from rest_framework import serializers


class StudentLoginSerializer(serializers.Serializer):
    index_number = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, min_length=8)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)


class SuperAdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)


class UniversalLoginSerializer(serializers.Serializer):
    identity = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)


class AuthPasswordRequiredSerializer(serializers.Serializer):
    requires_password = serializers.BooleanField()
    account_type = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    otp_request_uuid = serializers.UUIDField()
    otp_code = serializers.CharField(min_length=4, max_length=10)
    device_signals = serializers.DictField(required=False)


class OTPResendSerializer(serializers.Serializer):
    otp_request_uuid = serializers.UUIDField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthOTPChallengeSerializer(serializers.Serializer):
    requires_otp = serializers.BooleanField(required=False)
    otp_request_uuid = serializers.UUIDField(required=False)
    expires_at = serializers.DateTimeField(required=False)
    channel = serializers.CharField(required=False)
    masked_destination = serializers.CharField(required=False)
    mfa_required = serializers.BooleanField(required=False)
    requires_biometric = serializers.BooleanField(required=False)
    pending_auth_token = serializers.CharField(required=False)
    challenge = serializers.DictField(required=False)
    expires_in_seconds = serializers.IntegerField(required=False)


class AuthSuccessSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField(required=False)
    session_uuid = serializers.UUIDField(required=False)
    tokens = TokenResponseSerializer(required=False)
    redirect_path = serializers.CharField(required=False)
    requires_biometric = serializers.BooleanField(required=False)
    requires_enrollment = serializers.BooleanField(required=False)
    has_active_biometric_profile = serializers.BooleanField(required=False)
    pending_auth_token = serializers.CharField(required=False)
    challenge = serializers.DictField(required=False)
    expires_in_seconds = serializers.IntegerField(required=False)
    risk_score = serializers.FloatField(required=False)
    risk_reasons = serializers.ListField(child=serializers.CharField(), required=False)
    trusted_login = serializers.BooleanField(required=False)


class SessionSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    ip_address = serializers.CharField(allow_null=True)
    user_agent = serializers.CharField()
    is_active = serializers.BooleanField()
    expires_at = serializers.DateTimeField()
    last_activity_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()


class MFALogSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    event_type = serializers.CharField()
    ip_address = serializers.CharField(allow_null=True)
    user_agent = serializers.CharField()
    metadata = serializers.JSONField()
    created_at = serializers.DateTimeField()
