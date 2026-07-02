from rest_framework import serializers


class BallotSelectionSerializer(serializers.Serializer):
    position_uuid = serializers.UUIDField()
    candidate_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )


class SubmitBallotSerializer(serializers.Serializer):
    token_code = serializers.CharField(max_length=128)
    channel_name = serializers.ChoiceField(
        choices=["web", "ussd", "sms"],
        default="web",
    )
    selections = BallotSelectionSerializer(many=True)


class BallotConfirmationSerializer(serializers.Serializer):
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    confirmation_reference = serializers.CharField(required=False, allow_blank=True)
    positions_completed = serializers.ListField(child=serializers.CharField())
    positions_count = serializers.IntegerField()
    positions_skipped = serializers.IntegerField(required=False)
    votes_count = serializers.IntegerField(required=False)
    timestamp = serializers.DateTimeField()
    message = serializers.CharField()


class VoteVerificationSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    election_uuid = serializers.UUIDField()
    position_title = serializers.CharField(required=False)
    candidate_name = serializers.CharField(required=False)
    channel = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()


class VoteSummarySerializer(serializers.Serializer):
    position_title = serializers.CharField()
    candidate_name = serializers.CharField()
    channel = serializers.CharField()
    timestamp = serializers.DateTimeField()


class PreVotePresenceStatusSerializer(serializers.Serializer):
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    presence_required = serializers.BooleanField()
    presence_captured = serializers.BooleanField()
    captured_at = serializers.DateTimeField(required=False, allow_null=True)
    svt_id = serializers.UUIDField(required=False, allow_null=True)


class PreVotePresenceCaptureSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    svt_id = serializers.UUIDField()
    channel = serializers.CharField()
    captured_at = serializers.DateTimeField()
    message = serializers.CharField()


class PreVotePresenceSubmitSerializer(serializers.Serializer):
    token_code = serializers.CharField(max_length=128)
    channel = serializers.ChoiceField(
        choices=["web"],
        default="web",
    )
    image = serializers.ImageField()
