from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.voting.api.serializers import (
    BallotConfirmationSerializer,
    SubmitBallotSerializer,
    VoteSummarySerializer,
    VoteVerificationSerializer,
)
from apps.voting.permissions import CanVote
from apps.voting.services import ballot_service, vote_service


class VoteCastRateThrottle(UserRateThrottle):
    scope = "vote_cast"


def _client_meta(request):
    return request.META.get("REMOTE_ADDR"), request.META.get("HTTP_USER_AGENT", "")


class BallotView(APIView):
    permission_classes = [CanVote]

    def get(self, request, election_uuid):
        ip_address, user_agent = _client_meta(request)
        ballot = ballot_service.get_ballot(
            election_uuid=election_uuid,
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response({"success": True, "data": ballot})


class SubmitBallotView(APIView):
    permission_classes = [CanVote]
    throttle_classes = [VoteCastRateThrottle]

    def post(self, request, election_uuid):
        serializer = SubmitBallotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_address, user_agent = _client_meta(request)
        data = serializer.validated_data

        confirmation = vote_service.submit_ballot(
            election_uuid=election_uuid,
            user=request.user,
            token_code=data["token_code"],
            selections=data["selections"],
            channel_name=data["channel_name"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return Response(
            {"success": True, "data": BallotConfirmationSerializer(confirmation).data},
            status=status.HTTP_201_CREATED,
        )


class VerifyVoteView(APIView):
    permission_classes = [CanVote]

    def get(self, request, vote_id):
        ip_address, user_agent = _client_meta(request)
        result = vote_service.verify_vote(
            vote_id=vote_id,
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return Response(
            {"success": True, "data": VoteVerificationSerializer(result).data}
        )


class MyVotesView(APIView):
    permission_classes = [CanVote]

    def get(self, request, election_uuid):
        votes = vote_service.list_my_votes(election_uuid, request.user)
        data = [
            {
                "position_title": v.position.title,
                "candidate_name": v.candidate.full_name,
                "channel": v.channel.channel_name,
                "timestamp": v.timestamp,
            }
            for v in votes
        ]
        return Response(
            {"success": True, "data": VoteSummarySerializer(data, many=True).data}
        )
