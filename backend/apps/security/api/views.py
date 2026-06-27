from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.security.api.serializers import (
    SVTBallotSessionSerializer,
    SVTConfirmationSerializer,
    SVTIssueSerializer,
    SVTListSerializer,
    SVTReissueSerializer,
    SVTRevokeSerializer,
    SVTValidateSerializer,
    SVTVerificationResultSerializer,
    SVTVerifySerializer,
)
from apps.security.permissions import CanManageSVT, CanRequestSVT
from apps.security.services import svt_service


class SVTRequestRateThrottle(UserRateThrottle):
    scope = "svt_request"


def _client_meta(request):
    return request.META.get("REMOTE_ADDR"), request.META.get("HTTP_USER_AGENT", "")


class RequestSVTView(APIView):
    permission_classes = [CanRequestSVT]
    throttle_classes = [SVTRequestRateThrottle]

    def post(self, request, election_uuid):
        ip_address, user_agent = _client_meta(request)
        result = svt_service.request_svt(
            election_uuid=election_uuid,
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": SVTIssueSerializer(result).data},
            status=status.HTTP_201_CREATED,
        )


class ValidateSVTView(APIView):
    permission_classes = [CanRequestSVT]

    def post(self, request, election_uuid):
        serializer = SVTValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = svt_service.validate_and_start_ballot(
            token_code=serializer.validated_data["token_code"],
            user=request.user,
            election_uuid=election_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": SVTBallotSessionSerializer(result).data}
        )


class VerifyVoteBySVTView(APIView):
    permission_classes = [CanRequestSVT]

    def post(self, request):
        serializer = SVTVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        result = svt_service.verify_vote_by_svt(
            token_code=serializer.validated_data["token_code"],
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": SVTVerificationResultSerializer(result).data}
        )


class SVTConfirmationView(APIView):
    permission_classes = [CanRequestSVT]

    def post(self, request):
        serializer = SVTVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation = svt_service.get_ballot_confirmation_by_svt(
            token_code=serializer.validated_data["token_code"],
            user=request.user,
        )
        return Response(
            {"success": True, "data": SVTConfirmationSerializer(confirmation).data}
        )


class ElectionSVTListView(APIView):
    permission_classes = [CanManageSVT]

    def get(self, request, election_uuid):
        status_filter = request.query_params.get("status")
        tokens = svt_service.list_for_election(election_uuid, status=status_filter)
        data = [
            {
                "svt_id": t.svt_id,
                "user_uuid": t.user.uuid,
                "user_email": t.user.email,
                "user_name": t.user.get_full_name(),
                "election_uuid": t.election.uuid,
                "issued_at": t.issued_at,
                "expires_at": t.expires_at,
                "used_at": t.used_at,
                "status": t.status,
            }
            for t in tokens
        ]
        return Response(
            {"success": True, "data": SVTListSerializer(data, many=True).data}
        )


class RevokeSVTView(APIView):
    permission_classes = [CanManageSVT]

    def post(self, request, svt_id):
        ip_address, user_agent = _client_meta(request)
        svt = svt_service.revoke_svt(
            svt_id=svt_id,
            admin_user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {
                "success": True,
                "data": SVTRevokeSerializer(
                    {
                        "svt_id": svt.svt_id,
                        "status": svt.status,
                        "election_uuid": svt.election.uuid,
                        "user_uuid": svt.user.uuid,
                    }
                ).data,
            }
        )


class ReissueSVTView(APIView):
    permission_classes = [CanManageSVT]

    def post(self, request, svt_id):
        ip_address, user_agent = _client_meta(request)
        result = svt_service.reissue_svt(
            svt_id=svt_id,
            admin_user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": SVTReissueSerializer(result).data},
            status=status.HTTP_201_CREATED,
        )
