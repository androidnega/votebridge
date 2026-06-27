from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.candidates.api.serializers import (
    CandidateCreateSerializer,
    CandidateSerializer,
    CandidateUpdateSerializer,
)
from apps.candidates.permissions import CanManageCandidates
from apps.candidates.services import candidate_service
from apps.elections.api.views import StandardPagination


class CandidateViewSet(viewsets.ViewSet):
    permission_classes = [CanManageCandidates]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def list(self, request, election_uuid=None):
        status_filter = request.query_params.get("status")
        candidates = candidate_service.list_candidates(
            election_uuid=election_uuid,
            status=status_filter,
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(candidates, request)
        serializer = CandidateSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None, election_uuid=None):
        candidate = candidate_service.get_candidate(uuid)
        serializer = CandidateSerializer(candidate, context={"request": request})
        return Response({"success": True, "data": serializer.data})

    def create(self, request, election_uuid=None):
        serializer = CandidateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate = candidate_service.create_candidate(
            election_uuid=election_uuid,
            data=serializer.validated_data,
        )
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None, election_uuid=None):
        serializer = CandidateUpdateSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        candidate = candidate_service.update_candidate(uuid, serializer.validated_data)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    def update(self, request, uuid=None, election_uuid=None):
        serializer = CandidateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate = candidate_service.update_candidate(uuid, serializer.validated_data)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    def destroy(self, request, uuid=None, election_uuid=None):
        candidate_service.delete_candidate(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, uuid=None, election_uuid=None):
        candidate = candidate_service.approve_candidate(uuid)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, uuid=None, election_uuid=None):
        candidate = candidate_service.reject_candidate(uuid)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )


class GlobalCandidateViewSet(viewsets.ViewSet):
    """Candidate operations without election prefix in URL."""

    permission_classes = [CanManageCandidates]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def retrieve(self, request, uuid=None):
        candidate = candidate_service.get_candidate(uuid)
        serializer = CandidateSerializer(candidate, context={"request": request})
        return Response({"success": True, "data": serializer.data})

    def partial_update(self, request, uuid=None):
        serializer = CandidateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        candidate = candidate_service.update_candidate(uuid, serializer.validated_data)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    def update(self, request, uuid=None):
        serializer = CandidateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate = candidate_service.update_candidate(uuid, serializer.validated_data)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    def destroy(self, request, uuid=None):
        candidate_service.delete_candidate(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, uuid=None):
        candidate = candidate_service.approve_candidate(uuid)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, uuid=None):
        candidate = candidate_service.reject_candidate(uuid)
        return Response(
            {
                "success": True,
                "data": CandidateSerializer(candidate, context={"request": request}).data,
            }
        )
