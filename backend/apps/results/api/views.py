from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.accounts.permissions import _user_role_name
from apps.results.api.serializers import (
    CertifyResultSerializer,
    ElectionResultDetailSerializer,
    ElectionResultSummarySerializer,
    PublishedElectionResultSerializer,
)
from apps.results.models import ElectionResult
from apps.results.permissions import (
    CanArchiveResults,
    CanCertifyResults,
    CanGenerateResults,
    CanPublishResults,
    CanViewPublishedResults,
    CanViewResultReports,
)
from apps.results.repositories.election_result_repository import ElectionResultRepository
from apps.results.services.certification_service import certification_service
from apps.results.services.report_service import report_service
from apps.results.services.results_service import (
    result_integrity_service,
    results_generation_service,
)


def _serialize_summary(result: ElectionResult) -> dict:
    return {
        "uuid": result.uuid,
        "election_uuid": result.election.uuid,
        "election_title": result.election.title,
        "election_status": result.election.status,
        "result_status": result.status,
        "turnout_percentage": result.turnout_percentage,
        "total_votes_cast": result.total_votes_cast,
        "eligible_voters": result.eligible_voters,
        "generated_at": result.generated_at,
        "certified_at": result.certified_at,
        "published_at": result.published_at,
        "archived_at": result.archived_at,
    }


def _serialize_detail(result: ElectionResult) -> dict:
    data = _serialize_summary(result)
    data.update(
        {
            "standings": result.standings,
            "integrity_report": result.integrity_report,
            "result_hash": result.result_hash,
            "certification_notes": result.certification_notes,
            "fraud_acknowledged": result.fraud_acknowledged,
            "fraud_acknowledgment_notes": result.fraud_acknowledgment_notes,
            "generated_by_name": result.generated_by.get_full_name() if result.generated_by else None,
            "certified_by_name": result.certified_by.get_full_name() if result.certified_by else None,
            "published_by_name": result.published_by.get_full_name() if result.published_by else None,
        }
    )
    return data


def _serialize_published(result: ElectionResult) -> dict:
    return {
        "uuid": result.uuid,
        "election_uuid": result.election.uuid,
        "election_title": result.election.title,
        "standings": result.standings,
        "turnout_percentage": result.turnout_percentage,
        "total_votes_cast": result.total_votes_cast,
        "published_at": result.published_at,
    }


class ElectionResultListView(APIView):
    permission_classes = [CanViewPublishedResults]

    def get(self, request):
        role = _user_role_name(request.user)
        repo = ElectionResultRepository()

        if role in {Role.Name.ADMIN, Role.Name.SUPER_ADMIN}:
            status_filter = request.query_params.get("status")
            results = repo.list_filtered(status=status_filter)
        else:
            results = repo.list_filtered(published_only=True)

        data = [_serialize_summary(r) for r in results[:100]]
        return Response(
            {"success": True, "data": ElectionResultSummarySerializer(data, many=True).data}
        )


class ElectionResultDetailView(APIView):
    permission_classes = [CanViewPublishedResults]

    def get(self, request, election_uuid):
        result = certification_service.get_result_for_election(election_uuid)
        role = _user_role_name(request.user)

        if role in {Role.Name.STUDENT, Role.Name.CANDIDATE}:
            if result.status != ElectionResult.Status.PUBLISHED:
                return Response(
                    {"success": False, "error": {"code": "not_published", "message": "Results not published."}},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"success": True, "data": PublishedElectionResultSerializer(_serialize_published(result)).data}
            )

        return Response(
            {"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data}
        )


class GenerateResultsView(APIView):
    permission_classes = [CanGenerateResults]

    def post(self, request, election_uuid):
        result = results_generation_service.generate_results(election_uuid, request.user)
        return Response(
            {"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data},
            status=status.HTTP_201_CREATED,
        )


class PreviewResultsView(APIView):
    permission_classes = [CanViewResultReports]

    def get(self, request, election_uuid):
        result = certification_service.get_result_for_election(election_uuid)
        if not result.standings:
            return Response(
                {"success": False, "error": {"code": "not_generated", "message": "Results not generated yet."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data})


class IntegrityReportView(APIView):
    permission_classes = [CanViewResultReports]

    def get(self, request, election_uuid):
        result = certification_service.get_result_for_election(election_uuid)
        fraud_ack = request.query_params.get("acknowledge_fraud", "").lower() in ("true", "1", "yes")
        report = result_integrity_service.verify(result.election, fraud_acknowledged=fraud_ack)
        return Response({"success": True, "data": report})


class CertifyResultsView(APIView):
    permission_classes = [CanCertifyResults]

    def post(self, request, election_uuid):
        serializer = CertifyResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = certification_service.certify(
            election_uuid,
            request.user,
            notes=serializer.validated_data.get("notes", ""),
            acknowledge_fraud=serializer.validated_data.get("acknowledge_fraud", False),
            fraud_notes=serializer.validated_data.get("fraud_notes", ""),
        )
        return Response({"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data})


class PublishResultsView(APIView):
    permission_classes = [CanPublishResults]

    def post(self, request, election_uuid):
        result = certification_service.publish(election_uuid, request.user)
        return Response({"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data})


class ArchiveResultsView(APIView):
    permission_classes = [CanArchiveResults]

    def post(self, request, election_uuid):
        result = certification_service.archive(election_uuid, request.user)
        return Response({"success": True, "data": ElectionResultDetailSerializer(_serialize_detail(result)).data})


class CertificationQueueView(APIView):
    permission_classes = [CanCertifyResults]

    def get(self, request):
        results = ElectionResultRepository().list_certification_queue()
        data = [_serialize_summary(r) for r in results]
        return Response({"success": True, "data": ElectionResultSummarySerializer(data, many=True).data})


class PublicationQueueView(APIView):
    permission_classes = [CanPublishResults]

    def get(self, request):
        results = ElectionResultRepository().list_publication_queue()
        data = [_serialize_summary(r) for r in results]
        return Response({"success": True, "data": ElectionResultSummarySerializer(data, many=True).data})


class ArchiveQueueView(APIView):
    permission_classes = [CanArchiveResults]

    def get(self, request):
        results = ElectionResultRepository().list_archivable()
        data = [_serialize_summary(r) for r in results]
        return Response({"success": True, "data": ElectionResultSummarySerializer(data, many=True).data})


class ResultReportView(APIView):
    permission_classes = [CanViewResultReports]

    def get(self, request, election_uuid, report_format):
        result = certification_service.get_result_for_election(election_uuid)
        if not result.standings:
            return Response(
                {"success": False, "error": {"code": "not_generated", "message": "Results not generated yet."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = report_service.prepare(result, report_format)
        return Response({"success": True, "data": payload})
