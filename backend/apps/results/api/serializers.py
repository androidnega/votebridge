from rest_framework import serializers

from apps.results.models import ElectionResult


class ElectionResultSummarySerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    election_status = serializers.CharField()
    result_status = serializers.CharField()
    turnout_percentage = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_votes_cast = serializers.IntegerField()
    eligible_voters = serializers.IntegerField()
    generated_at = serializers.DateTimeField(allow_null=True)
    certified_at = serializers.DateTimeField(allow_null=True)
    published_at = serializers.DateTimeField(allow_null=True)
    archived_at = serializers.DateTimeField(allow_null=True)


class ElectionResultDetailSerializer(ElectionResultSummarySerializer):
    standings = serializers.JSONField()
    integrity_report = serializers.JSONField()
    result_hash = serializers.CharField()
    certification_notes = serializers.CharField()
    fraud_acknowledged = serializers.BooleanField()
    fraud_acknowledgment_notes = serializers.CharField()
    generated_by_name = serializers.CharField(allow_null=True)
    certified_by_name = serializers.CharField(allow_null=True)
    published_by_name = serializers.CharField(allow_null=True)


class PublishedElectionResultSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    election_uuid = serializers.UUIDField()
    election_title = serializers.CharField()
    standings = serializers.JSONField()
    turnout_percentage = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_votes_cast = serializers.IntegerField()
    published_at = serializers.DateTimeField()


class CertifyResultSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    acknowledge_fraud = serializers.BooleanField(required=False, default=False)
    fraud_notes = serializers.CharField(required=False, allow_blank=True, default="")


class ReportFormatSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["csv", "pdf", "excel", "xlsx"])
