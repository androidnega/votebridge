from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.system.permissions import CanAccessSystemControlCenter
from apps.system.services.step_up_service import step_up_auth_service
from apps.system.services.system_service import (
    backup_service,
    environment_service,
    feature_flag_service,
    institution_service,
    maintenance_service,
    provider_management_service,
    storage_service,
    system_overview_service,
    system_settings_service,
)
from apps.system.validators import validate_category, validate_setting_key, validate_step_up_token
from core.client_meta import get_client_ip, get_user_agent


class SystemOverviewView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": system_overview_service.get_overview()})


class PublicBrandingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"success": True, "data": system_settings_service.get_public_branding()})


class MaintenancePublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"success": True, "data": maintenance_service.get_state()})


class StepUpChallengeView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def post(self, request):
        data = step_up_auth_service.request_challenge(
            request.user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return Response({"success": True, "data": data})


class StepUpVerifyView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def post(self, request):
        challenge_id = request.data.get("challenge_id")
        code = request.data.get("code")
        data = step_up_auth_service.verify_challenge(
            request.user,
            challenge_id=challenge_id,
            code=code,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return Response({"success": True, "data": data})


class InstitutionSettingsView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": institution_service.get_profile()})

    def patch(self, request):
        preview = request.query_params.get("preview") == "true"
        data = institution_service.update_profile(
            request.user,
            request.data,
            preview=preview,
            request=request,
        )
        return Response({"success": True, "data": data})


class SettingsCategoryView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request, category):
        category = validate_category(category)
        return Response({"success": True, "data": system_settings_service.get_category(category)})

    def patch(self, request, category):
        category = validate_category(category)
        step_up_token = request.data.get("step_up_token")
        updates = request.data.get("settings") or request.data.get("updates") or {}
        reason = request.data.get("reason", "")
        data = system_settings_service.update_settings(
            request.user,
            category,
            updates,
            step_up_token=step_up_token,
            reason=reason,
            request=request,
        )
        return Response({"success": True, "data": data})


class SettingRevisionsView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request, key):
        key = validate_setting_key(key)
        return Response({"success": True, "data": system_settings_service.list_revisions(key)})

    def post(self, request, key):
        validate_setting_key(key)
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        revision_uuid = request.data.get("revision_uuid")
        data = system_settings_service.rollback(
            request.user,
            revision_uuid,
            step_up_token=step_up_token,
            request=request,
        )
        return Response({"success": True, "data": data})


class FeatureFlagsView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": feature_flag_service.list_flags()})

    def patch(self, request, key):
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        enabled = bool(request.data.get("enabled"))
        data = feature_flag_service.update_flag(
            request.user,
            key,
            enabled,
            step_up_token=step_up_token,
            request=request,
        )
        return Response({"success": True, "data": data})


class MaintenanceSettingsView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": maintenance_service.get_state()})

    def patch(self, request):
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        data = maintenance_service.update_state(
            request.user,
            request.data,
            step_up_token=step_up_token,
            request=request,
        )
        return Response({"success": True, "data": data})


class ProvidersListView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        provider_type = request.query_params.get("type")
        return Response({"success": True, "data": provider_management_service.list_providers(provider_type)})


class ProviderDetailView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def patch(self, request, provider_uuid):
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        payload = {k: v for k, v in request.data.items() if k != "step_up_token"}
        data = provider_management_service.update_provider(
            request.user,
            provider_uuid,
            payload,
            step_up_token=step_up_token,
            request=request,
        )
        return Response({"success": True, "data": data})

    def post(self, request, provider_uuid):
        data = provider_management_service.test_provider(request.user, provider_uuid, request=request)
        return Response({"success": True, "data": data})


class StorageView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": storage_service.get_usage()})

    def post(self, request):
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        data = storage_service.cleanup_temp(request.user, step_up_token=step_up_token, request=request)
        return Response({"success": True, "data": data})


class BackupListView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": backup_service.list_backups()})

    def post(self, request):
        step_up_token = validate_step_up_token(request.data.get("step_up_token"))
        data = backup_service.create_backup(
            request.user,
            backup_type=request.data.get("backup_type", "manual"),
            step_up_token=step_up_token,
            request=request,
        )
        return Response({"success": True, "data": data})


class BackupDetailView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def post(self, request, backup_uuid):
        action = request.data.get("action", "verify")
        if action == "verify":
            data = backup_service.verify_backup(request.user, backup_uuid, request=request)
            return Response({"success": True, "data": data})
        return Response({"success": False, "error": {"message": "Unsupported action"}}, status=400)


class EnvironmentView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": environment_service.get_info()})


class LicenseView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response({"success": True, "data": system_overview_service.get_license()})


class RuntimeConfigView(APIView):
    permission_classes = [CanAccessSystemControlCenter]

    def get(self, request):
        return Response(
            {
                "success": True,
                "data": {
                    "runtime": system_settings_service.get_category("runtime"),
                    "note": "Changes apply immediately without application restart where supported.",
                },
            }
        )
