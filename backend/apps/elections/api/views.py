from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.elections.api.serializers import (
    BulkEligibilitySerializer,
    ElectionCreateSerializer,
    ElectionSerializer,
    PositionCreateUpdateSerializer,
    PositionSerializer,
    VoterEligibilityCreateSerializer,
    VoterEligibilitySerializer,
    VoterEligibilityUpdateSerializer,
    VotingChannelSerializer,
)
from apps.elections.permissions import (
    CanManageElections,
    CanManagePositions,
    CanManageVoterEligibility,
    CanManageVotingChannels,
)
from apps.elections.services import (
    election_readiness_service,
    election_service,
    eligibility_service,
    position_service,
    voting_channel_service,
)
from apps.security.models import AuditLog
from apps.security.services.monitoring_service import monitoring_service
from core.client_meta import get_client_context


def _log_election_monitoring(request, event_type, election=None, metadata=None):
    ctx = get_client_context(request)
    meta = dict(metadata or {})
    if election:
        meta.setdefault("election_uuid", str(election.uuid))
    monitoring_service.record_event(
        event_type=event_type,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        browser_fingerprint=ctx["browser_fingerprint"],
        metadata=meta,
        election_uuid=meta.get("election_uuid"),
    )


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class ElectionViewSet(viewsets.ViewSet):
    permission_classes = [CanManageElections]

    def list(self, request):
        query = request.query_params.get("search")
        status_filter = request.query_params.get("status")
        election_type = request.query_params.get("election_type")

        elections = election_service.list_elections(
            query=query,
            status=status_filter,
            election_type=election_type,
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(elections, request)
        serializer = ElectionSerializer(page, many=True)
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None):
        election = election_service.get_election(uuid)
        _log_election_monitoring(request, AuditLog.EventType.ELECTION_ACCESSED, election=election)
        serializer = ElectionSerializer(election)
        return Response({"success": True, "data": serializer.data})

    def create(self, request):
        serializer = ElectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        election = election_service.create_election(
            created_by=request.user,
            data=serializer.validated_data,
        )
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_CREATED,
            election=election,
            metadata={"action": "create"},
        )
        return Response(
            {"success": True, "data": ElectionSerializer(election).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None):
        serializer = ElectionCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        election = election_service.update_election(uuid, serializer.validated_data)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_UPDATED,
            election=election,
            metadata={"action": "partial_update"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    def update(self, request, uuid=None):
        serializer = ElectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        election = election_service.update_election(uuid, serializer.validated_data)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_UPDATED,
            election=election,
            metadata={"action": "update"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    def destroy(self, request, uuid=None):
        election = election_service.get_election(uuid)
        election_service.delete_election(uuid)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_DELETED,
            election=election,
            metadata={"action": "delete"},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="schedule")
    def schedule(self, request, uuid=None):
        election = election_service.schedule_election(uuid)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            election=election,
            metadata={"new_status": election.status, "action": "schedule"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    @action(detail=True, methods=["get"], url_path="readiness")
    def readiness(self, request, uuid=None):
        election = election_service.get_election(uuid)
        report = election_readiness_service.assess(election, actor=request.user)
        return Response({"success": True, "data": report.to_dict()})

    @action(detail=True, methods=["post"], url_path="open")
    def open_election(self, request, uuid=None):
        election = election_service.open_election(uuid, actor=request.user)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            election=election,
            metadata={"new_status": election.status, "action": "open"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    @action(detail=True, methods=["post"], url_path="pause")
    def pause(self, request, uuid=None):
        election = election_service.pause_election(uuid)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            election=election,
            metadata={"new_status": election.status, "action": "pause"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, uuid=None):
        election = election_service.close_election(uuid)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            election=election,
            metadata={"new_status": election.status, "action": "close"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, uuid=None):
        election = election_service.archive_election(uuid)
        _log_election_monitoring(
            request,
            AuditLog.EventType.ELECTION_STATUS_CHANGED,
            election=election,
            metadata={"new_status": election.status, "action": "archive"},
        )
        return Response({"success": True, "data": ElectionSerializer(election).data})


class VotingChannelViewSet(viewsets.ViewSet):
    permission_classes = [CanManageVotingChannels]

    def list(self, request):
        active_only = request.query_params.get("active_only", "").lower() in (
            "true",
            "1",
            "yes",
        )
        channels = voting_channel_service.list_channels(active_only=active_only)
        serializer = VotingChannelSerializer(channels, many=True)
        return Response({"success": True, "data": serializer.data})

    def retrieve(self, request, uuid=None):
        channel = voting_channel_service.get_channel(uuid)
        serializer = VotingChannelSerializer(channel)
        return Response({"success": True, "data": serializer.data})

    def create(self, request):
        serializer = VotingChannelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = voting_channel_service.create_channel(
            channel_name=serializer.validated_data["channel_name"],
            is_active=serializer.validated_data.get("is_active", True),
        )
        return Response(
            {"success": True, "data": VotingChannelSerializer(channel).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None):
        serializer = VotingChannelSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        channel = voting_channel_service.update_channel(uuid, **serializer.validated_data)
        return Response({"success": True, "data": VotingChannelSerializer(channel).data})

    def destroy(self, request, uuid=None):
        voting_channel_service.delete_channel(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PositionViewSet(viewsets.ViewSet):
    permission_classes = [CanManagePositions]

    def list(self, request, election_uuid=None):
        query = request.query_params.get("search")
        is_active = request.query_params.get("is_active")
        is_active_bool = None
        if is_active is not None:
            is_active_bool = is_active.lower() in ("true", "1", "yes")

        positions = position_service.list_positions(
            election_uuid=election_uuid,
            query=query,
            is_active=is_active_bool,
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(positions, request)
        serializer = PositionSerializer(page, many=True)
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None, election_uuid=None):
        position = position_service.get_position(uuid)
        serializer = PositionSerializer(position)
        return Response({"success": True, "data": serializer.data})

    def create(self, request, election_uuid=None):
        serializer = PositionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        position = position_service.create_position(
            election_uuid=election_uuid,
            data=serializer.validated_data,
        )
        return Response(
            {"success": True, "data": PositionSerializer(position).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None, election_uuid=None):
        serializer = PositionCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        position = position_service.update_position(uuid, serializer.validated_data)
        return Response({"success": True, "data": PositionSerializer(position).data})

    def update(self, request, uuid=None, election_uuid=None):
        serializer = PositionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        position = position_service.update_position(uuid, serializer.validated_data)
        return Response({"success": True, "data": PositionSerializer(position).data})

    def destroy(self, request, uuid=None, election_uuid=None):
        position_service.delete_position(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VoterEligibilityViewSet(viewsets.ViewSet):
    permission_classes = [CanManageVoterEligibility]

    def list(self, request, election_uuid=None):
        query = request.query_params.get("search")
        is_eligible = request.query_params.get("is_eligible")
        is_eligible_bool = None
        if is_eligible is not None:
            is_eligible_bool = is_eligible.lower() in ("true", "1", "yes")

        records = eligibility_service.list_eligibilities(
            election_uuid=election_uuid,
            query=query,
            is_eligible=is_eligible_bool,
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(records, request)
        serializer = VoterEligibilitySerializer(page, many=True)
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None, election_uuid=None):
        record = eligibility_service.get_eligibility(uuid)
        serializer = VoterEligibilitySerializer(record)
        return Response({"success": True, "data": serializer.data})

    def create(self, request, election_uuid=None):
        serializer = VoterEligibilityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        record = eligibility_service.create_eligibility(
            election_uuid=election_uuid,
            user_uuid=data["user_uuid"],
            data=data,
            verified_by=request.user,
        )
        return Response(
            {"success": True, "data": VoterEligibilitySerializer(record).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None, election_uuid=None):
        serializer = VoterEligibilityUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        record = eligibility_service.update_eligibility(
            uuid,
            serializer.validated_data,
            verified_by=request.user,
        )
        return Response({"success": True, "data": VoterEligibilitySerializer(record).data})

    def update(self, request, uuid=None, election_uuid=None):
        serializer = VoterEligibilityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = eligibility_service.update_eligibility(
            uuid,
            serializer.validated_data,
            verified_by=request.user,
        )
        return Response({"success": True, "data": VoterEligibilitySerializer(record).data})

    def destroy(self, request, uuid=None, election_uuid=None):
        eligibility_service.delete_eligibility(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_manage(self, request, election_uuid=None):
        serializer = BulkEligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        records = eligibility_service.bulk_set_eligibility(
            election_uuid=election_uuid,
            user_uuids=data["user_uuids"],
            is_eligible=data["is_eligible"],
            eligibility_reason=data.get("eligibility_reason", ""),
            verified_by=request.user,
        )
        return Response(
            {
                "success": True,
                "data": VoterEligibilitySerializer(records, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class PublicCampusStatusView(APIView):
    """Public election phase summary — no vote totals or rankings."""

    permission_classes = [AllowAny]

    def get(self, request):
        data = election_service.get_public_campus_status()
        return Response({"success": True, "data": data})


class PublicElectionPortalView(APIView):
    """Public election portal — transparency data for landing and observer views."""

    permission_classes = [AllowAny]

    def get(self, request):
        data = election_service.get_public_election_portal()
        return Response({"success": True, "data": data})

