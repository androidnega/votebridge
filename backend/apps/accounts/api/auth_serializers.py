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
    password = serializers.CharField(write_only=True, min_length=8)


class OTPVerifySerializer(serializers.Serializer):
    otp_request_uuid = serializers.UUIDField()
    otp_code = serializers.CharField(min_length=4, max_length=10)


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
    requires_otp = serializers.BooleanField()
    otp_request_uuid = serializers.UUIDField()
    expires_at = serializers.DateTimeField()
    channel = serializers.CharField()
    mfa_required = serializers.BooleanField(required=False)


class AuthSuccessSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField()
    session_uuid = serializers.UUIDField()
    tokens = TokenResponseSerializer()
    redirect_path = serializers.CharField()


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
