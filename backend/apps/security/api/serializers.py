from rest_framework import serializers


class SVTIssueSerializer(serializers.Serializer):
    svt_id = serializers.UUIDField()
    token_code = serializers.CharField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    issued_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    status = serializers.CharField()
    message = serializers.CharField()


class SVTValidateSerializer(serializers.Serializer):
    token_code = serializers.CharField(max_length=128)


class SVTBallotSessionSerializer(serializers.Serializer):
    svt_id = serializers.UUIDField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    status = serializers.CharField()
    expires_at = serializers.DateTimeField()
    message = serializers.CharField()


class SVTVerifySerializer(serializers.Serializer):
    token_code = serializers.CharField(max_length=128)


class SVTVerificationResultSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    positions_completed = serializers.ListField(child=serializers.CharField())
    positions_count = serializers.IntegerField()
    votes_count = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    svt_status = serializers.CharField()
    used_at = serializers.DateTimeField(allow_null=True)


class SVTConfirmationSerializer(serializers.Serializer):
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    positions_completed = serializers.ListField(child=serializers.CharField())
    positions_count = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    svt_status = serializers.CharField()
    used_at = serializers.DateTimeField(allow_null=True)
    message = serializers.CharField()


class SVTListSerializer(serializers.Serializer):
    svt_id = serializers.UUIDField()
    user_uuid = serializers.UUIDField()
    user_email = serializers.EmailField()
    user_name = serializers.CharField()
    election_uuid = serializers.UUIDField()
    issued_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    used_at = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()


class SVTReissueSerializer(serializers.Serializer):
    svt_id = serializers.UUIDField()
    token_code = serializers.CharField()
    election_uuid = serializers.UUIDField()
    user_uuid = serializers.UUIDField()
    user_email = serializers.EmailField()
    issued_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    status = serializers.CharField()
    replaced_svt_id = serializers.UUIDField()


class SVTRevokeSerializer(serializers.Serializer):
    svt_id = serializers.UUIDField()
    status = serializers.CharField()
    election_uuid = serializers.UUIDField()
    user_uuid = serializers.UUIDField()
