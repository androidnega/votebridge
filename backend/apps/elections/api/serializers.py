from rest_framework import serializers

from django.core.exceptions import ValidationError as DjangoValidationError

from apps.elections.models import Election, Position, VoterEligibility, VotingChannel
from apps.elections.validators import validate_election_dates


class ElectionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    election_type_display = serializers.CharField(
        source="get_election_type_display",
        read_only=True,
    )
    created_by_uuid = serializers.UUIDField(source="created_by.uuid", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    candidate_count = serializers.SerializerMethodField()
    approved_candidate_count = serializers.SerializerMethodField()
    position_count = serializers.SerializerMethodField()
    is_read_only = serializers.BooleanField(read_only=True)

    class Meta:
        model = Election
        fields = [
            "uuid",
            "title",
            "description",
            "election_type",
            "election_type_display",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "allow_web_voting",
            "allow_ussd_voting",
            "allow_sms_notifications",
            "created_by_uuid",
            "created_by_name",
            "candidate_count",
            "approved_candidate_count",
            "position_count",
            "is_read_only",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "status",
            "created_by_uuid",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()

    def get_candidate_count(self, obj):
        return obj.candidates.count()

    def get_approved_candidate_count(self, obj):
        return obj.candidates.filter(status="approved").count()

    def get_position_count(self, obj):
        return obj.positions.count()

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if self.instance:
            start = start or self.instance.start_date
            end = end or self.instance.end_date
        try:
            validate_election_dates(start, end)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class ElectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = [
            "title",
            "description",
            "election_type",
            "start_date",
            "end_date",
            "allow_web_voting",
            "allow_ussd_voting",
            "allow_sms_notifications",
        ]

    def validate(self, attrs):
        try:
            validate_election_dates(attrs.get("start_date"), attrs.get("end_date"))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class VotingChannelSerializer(serializers.ModelSerializer):
    channel_name_display = serializers.CharField(
        source="get_channel_name_display",
        read_only=True,
    )

    class Meta:
        model = VotingChannel
        fields = [
            "uuid",
            "channel_name",
            "channel_name_display",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["uuid", "created_at"]


class PositionSerializer(serializers.ModelSerializer):
    election_uuid = serializers.UUIDField(source="election.uuid", read_only=True)
    choice_type = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = [
            "uuid",
            "election_uuid",
            "title",
            "description",
            "max_votes_allowed",
            "display_order",
            "is_active",
            "is_votable",
            "choice_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def get_choice_type(self, obj):
        return "single" if obj.is_single_choice else "multi"


class PositionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            "title",
            "description",
            "max_votes_allowed",
            "display_order",
            "is_active",
            "is_votable",
        ]


class VoterEligibilitySerializer(serializers.ModelSerializer):
    election_uuid = serializers.UUIDField(source="election.uuid", read_only=True)
    user_uuid = serializers.UUIDField(source="user.uuid", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    user_index_number = serializers.CharField(source="user.index_number", read_only=True)
    verified_by_uuid = serializers.UUIDField(
        source="verified_by.uuid",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = VoterEligibility
        fields = [
            "uuid",
            "election_uuid",
            "user_uuid",
            "user_email",
            "user_name",
            "user_index_number",
            "is_eligible",
            "eligibility_reason",
            "verified_by_uuid",
            "verified_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "verified_by_uuid",
            "verified_at",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name()


class VoterEligibilityCreateSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField()
    is_eligible = serializers.BooleanField(default=True)
    eligibility_reason = serializers.CharField(required=False, allow_blank=True)


class VoterEligibilityUpdateSerializer(serializers.Serializer):
    is_eligible = serializers.BooleanField(required=False)
    eligibility_reason = serializers.CharField(required=False, allow_blank=True)


class BulkEligibilitySerializer(serializers.Serializer):
    user_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )
    is_eligible = serializers.BooleanField()
    eligibility_reason = serializers.CharField(required=False, allow_blank=True)
