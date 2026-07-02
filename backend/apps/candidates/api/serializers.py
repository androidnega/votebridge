from rest_framework import serializers

from apps.candidates.models import Candidate


class PositionSummarySerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    title = serializers.CharField()
    max_votes_allowed = serializers.IntegerField()


class CandidateSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    election_uuid = serializers.UUIDField(source="election.uuid", read_only=True)
    election_title = serializers.CharField(source="election.title", read_only=True)
    position_uuid = serializers.UUIDField(source="position.uuid", read_only=True)
    position_title = serializers.CharField(source="position.title", read_only=True)
    user_uuid = serializers.UUIDField(source="user.uuid", read_only=True, allow_null=True)
    index_number = serializers.CharField(source="user.index_number", read_only=True, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            "uuid",
            "election_uuid",
            "election_title",
            "position_uuid",
            "position_title",
            "user_uuid",
            "index_number",
            "full_name",
            "department",
            "manifesto",
            "image",
            "image_url",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = ["uuid", "status", "created_at"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CandidateCreateSerializer(serializers.Serializer):
    position_uuid = serializers.UUIDField()
    user_uuid = serializers.UUIDField(required=False, allow_null=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True, max_length=150)
    manifesto = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False)

    def validate(self, attrs):
        if not attrs.get("user_uuid") and not (attrs.get("full_name") or "").strip():
            raise serializers.ValidationError(
                {"full_name": "Provide a student or enter a full name."}
            )
        return attrs


class CandidateUpdateSerializer(serializers.Serializer):
    position_uuid = serializers.UUIDField(required=False)
    user_uuid = serializers.UUIDField(required=False, allow_null=True)
    full_name = serializers.CharField(required=False, max_length=255)
    department = serializers.CharField(required=False, allow_blank=True, max_length=150)
    manifesto = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False)
