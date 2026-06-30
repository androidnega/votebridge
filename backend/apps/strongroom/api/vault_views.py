from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin
from apps.elections.repositories.election_repository import ElectionRepository
from apps.strongroom.permissions import CanManageStrongroom, CanViewStrongroom
from apps.strongroom.services.vault_access_service import vault_access_service
from apps.strongroom.services.vault_committee_service import vault_committee_service
from apps.strongroom.services.vault_session_service import vault_session_service


def _election_or_404(election_uuid):
    election = ElectionRepository().get_by_uuid(election_uuid)
    if not election:
        return None
    return election


class CommitteeView(APIView):
    """Nominate and review strong room committee configuration."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminOrSuperAdmin()]
        if self.request.method == "POST":
            return [IsAdminOrSuperAdmin()]
        return super().get_permissions()

    def get(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_committee_service.get_committee(election)
        return Response({"success": True, "data": data})

    def post(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_committee_service.configure_committee(
            election,
            actor=request.user,
            member_user_uuids=request.data.get("member_user_uuids", []),
            session_duration_hours=int(request.data.get("session_duration_hours", 2)),
            access_policy=request.data.get("access_policy", "multi_custodian"),
        )
        return Response({"success": True, "data": data})


class CommitteeSubmitView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_committee_service.submit_for_approval(election, actor=request.user)
        return Response({"success": True, "data": data})


class CommitteeApproveView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_committee_service.approve_committee(election, actor=request.user)
        return Response({"success": True, "data": data})


class VaultAccessRequestListCreateView(APIView):
    permission_classes = [CanManageStrongroom]

    def get(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_access_service.list_requests(election)
        return Response({"success": True, "data": data})

    def post(self, request, election_uuid):
        election = _election_or_404(election_uuid)
        if not election:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Election not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_access_service.create_request(
            election,
            actor=request.user,
            reason=request.data.get("reason", ""),
            justification=request.data.get("justification", ""),
        )
        return Response({"success": True, "data": data}, status=status.HTTP_201_CREATED)


class VaultAccessRequestReviewView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, election_uuid, request_uuid):
        access_request = vault_access_service.get_request(request_uuid)
        if not access_request or str(access_request.election.uuid) != str(election_uuid):
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Access request not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        action = request.data.get("action", "approve")
        if action == "deny":
            data = vault_access_service.deny_request(access_request, actor=request.user)
        else:
            data = vault_access_service.approve_request(access_request, actor=request.user)
        return Response({"success": True, "data": data})


class VaultSessionStartView(APIView):
    permission_classes = [CanManageStrongroom]

    def post(self, request, election_uuid):
        access_request = vault_access_service.get_request(request.data.get("access_request_uuid"))
        if not access_request or str(access_request.election.uuid) != str(election_uuid):
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Access request not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_session_service.start_session(access_request, actor=request.user)
        return Response({"success": True, "data": data}, status=status.HTTP_201_CREATED)


class VaultSessionDetailView(APIView):
    permission_classes = [CanViewStrongroom]

    def get(self, request, session_uuid):
        data = vault_session_service.get_session(session_uuid, actor=request.user)
        if data["status"] != "active":
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "vault_not_active",
                        "message": "Vault session is not active.",
                    },
                    "data": data,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"success": True, "data": data})


class VaultSessionAuthenticateView(APIView):
    permission_classes = [CanManageStrongroom]

    def post(self, request, session_uuid):
        from apps.strongroom.repositories.vault_repository import VaultSessionRepository

        session = VaultSessionRepository().get_by_uuid(session_uuid)
        if not session:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Session not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = vault_session_service.authenticate_custodian(
            session,
            identifier=request.data.get("identifier", ""),
            password=request.data.get("password", ""),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response({"success": True, "data": data})


class VaultSessionStatusView(APIView):
    """Terminal polling — returns session state without requiring active vault."""

    permission_classes = [CanManageStrongroom]

    def get(self, request, session_uuid):
        data = vault_session_service.get_session(session_uuid, actor=request.user)
        return Response({"success": True, "data": data})


class VaultSessionCloseView(APIView):
    permission_classes = [CanManageStrongroom]

    def post(self, request, session_uuid):
        from apps.strongroom.repositories.vault_repository import VaultSessionRepository

        session = VaultSessionRepository().get_by_uuid(session_uuid)
        if not session:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Session not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        closed = vault_session_service.close_session(session, actor=request.user)
        data = vault_session_service.get_session(closed.uuid, actor=request.user)
        return Response({"success": True, "data": data})
