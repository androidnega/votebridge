from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.strongroom.permissions import CanManageStrongroom, CanViewStrongroom
from apps.strongroom.repositories.strongroom_repository import ElectionSealRepository
from apps.strongroom.services.integrity_verification_service import integrity_verification_service
from apps.strongroom.services.strongroom_service import election_seal_service
from apps.elections.repositories.election_repository import ElectionRepository


class StrongroomDashboardView(APIView):
    permission_classes = [CanViewStrongroom]

    def get(self, request, election_uuid):
        data = integrity_verification_service.get_dashboard(election_uuid)
        return Response({"success": True, "data": data})


class StrongroomListView(APIView):
    permission_classes = [CanViewStrongroom]

    def get(self, request):
        repo = ElectionSealRepository()
        seals = repo.get_queryset().order_by("-updated_at")[:50]
        data = [
            {
                "election_uuid": str(s.election.uuid),
                "election_title": s.election.title,
                "seal_status": s.status,
                "sealed_at": s.sealed_at,
                "locked_at": s.locked_at,
                "verification_hash": s.verification_hash,
            }
            for s in seals
        ]
        return Response({"success": True, "data": data})


class CustodyTimelineView(APIView):
    permission_classes = [CanViewStrongroom]

    def get(self, request, election_uuid):
        dashboard = integrity_verification_service.get_dashboard(election_uuid)
        return Response({"success": True, "data": dashboard["custody_timeline"]})


class VerifyIntegrityView(APIView):
    permission_classes = [CanManageStrongroom]

    def post(self, request, election_uuid):
        from apps.biometrics.services.policy_service import biometric_policy_service
        from apps.biometrics.services.session_service import biometric_session_service

        if biometric_policy_service.requires_step_up(request.user, "strongroom_access"):
            token = request.data.get("high_assurance_token") or request.data.get("step_up_token")
            if request.data.get("high_assurance_token"):
                biometric_session_service.validate_session(request.user, token)
                biometric_session_service.consume_session(request.user, token)
            else:
                from apps.system.services.step_up_service import step_up_auth_service

                step_up_auth_service.validate_token(request.user, token or "")
                step_up_auth_service.consume_token(request.user, token or "")

        report = integrity_verification_service.verify_full(election_uuid, actor=request.user)
        return Response({"success": True, "data": report})


class LockElectionView(APIView):
    permission_classes = [CanManageStrongroom]

    def post(self, request, election_uuid):
        election = ElectionRepository().get_by_uuid(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        seal = election_seal_service.lock_election(election, actor=request.user)
        return Response(
            {
                "success": True,
                "data": {
                    "election_uuid": str(election.uuid),
                    "seal_status": seal.status,
                    "locked_at": seal.locked_at,
                },
            }
        )


class PublicVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        election_uuid = request.data.get("election_uuid")
        verification_hash = request.data.get("verification_hash", "").strip()
        if not election_uuid or not verification_hash:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "validation_error",
                        "message": "election_uuid and verification_hash are required.",
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        report = integrity_verification_service.verify_public(election_uuid, verification_hash)
        return Response({"success": True, "data": report})
