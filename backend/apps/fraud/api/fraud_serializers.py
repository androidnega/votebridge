from rest_framework import serializers


class FraudCaseSerializer(serializers.Serializer):
    fraud_case_id = serializers.UUIDField()
    election_uuid = serializers.UUIDField(allow_null=True)
    election_title = serializers.CharField(allow_null=True)
    user_uuid = serializers.UUIDField(allow_null=True)
    user_email = serializers.EmailField(allow_null=True)
    user_name = serializers.CharField(allow_null=True)
    related_alert_id = serializers.UUIDField()
    alert_type = serializers.CharField()
    alert_title = serializers.CharField()
    risk_score = serializers.IntegerField()
    severity = serializers.CharField()
    status = serializers.CharField()
    investigation_notes = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class FraudIntegrityReportSerializer(serializers.Serializer):
    total_fraud_cases = serializers.IntegerField()
    open_cases = serializers.IntegerField()
    resolved_cases = serializers.IntegerField()
    high_risk_cases = serializers.IntegerField()
    critical_cases = serializers.IntegerField()
    election_uuid = serializers.UUIDField(required=False, allow_null=True)


class InvestigationNoteSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=5000)


class CaseActionSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")


class TimelineEventSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    event_type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    source = serializers.CharField()
