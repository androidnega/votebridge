import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import django
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from apps.elections.models import Election
from apps.notifications.services.communication_service import communication_service
from apps.operations.services.operations_service import operations_health_service
from apps.security.models import AuditLog
from apps.security.services.monitoring_service import monitoring_service
from apps.system.constants import (
    APP_VERSION,
    BUILD_NUMBER,
    RELEASE_CHANNEL,
    SENSITIVE_ACTIONS,
    SENSITIVE_SETTING_KEYS,
    SETTING_CATEGORIES,
)
from apps.system.models import BackupRecord, FeatureFlag, InstitutionProfile, MaintenanceState
from apps.system.repositories.system_repository import (
    BackupRepository,
    FeatureFlagRepository,
    InstitutionRepository,
    MaintenanceRepository,
    ProviderRepository,
    SettingRevisionRepository,
    SystemSettingRepository,
)
from apps.system.services.step_up_service import step_up_auth_service
from apps.system.utils import encrypt_secret, invalidate_settings_cache, mask_config, mask_secret
from core.client_meta import get_client_ip
from core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger("votebridge")

DEFAULT_SETTINGS = {
    "identity_assurance": {
        "enable_face_verification": {"value": True, "description": "Enable face verification for privileged users"},
        "enable_passive_liveness": {"value": True, "description": "Detect printed photos and replay attacks"},
        "enable_active_liveness": {"value": True, "description": "Require challenge completion"},
        "enable_blink_challenge": {"value": True, "description": "Allow blink challenges"},
        "enable_left_turn": {"value": True, "description": "Allow left turn challenges"},
        "enable_right_turn": {"value": True, "description": "Allow right turn challenges"},
        "random_challenge": {"value": True, "description": "Randomly select challenge type"},
        "matching_threshold": {"value": 0.62, "description": "Cosine similarity threshold for face match"},
        "liveness_threshold": {"value": 0.70, "description": "Minimum passive liveness score"},
        "maximum_attempts": {"value": 5, "description": "Failed attempts before lockout"},
        "lockout_minutes": {"value": 30, "description": "Biometric lockout duration (minutes)"},
        "session_timeout_minutes": {"value": 15, "description": "High assurance session lifetime (minutes)"},
        "enable_verification_snapshots": {"value": False, "description": "Store verification snapshots (disabled by default)"},
        "enable_confidence_logging": {"value": True, "description": "Log match confidence in audit trail"},
        "enable_audit": {"value": True, "description": "Record biometric audit events"},
        "enable_trusted_devices": {"value": True, "description": "Enable trusted device recognition"},
        "enable_risk_based_authentication": {"value": True, "description": "Require biometrics only when risk is elevated"},
        "trusted_device_expiration_days": {"value": 90, "description": "Trusted device expiration (days)"},
        "max_trusted_devices_per_user": {"value": 5, "description": "Maximum trusted devices per administrator"},
        "require_biometrics_for_new_device": {"value": True, "description": "Require biometrics for unrecognized devices"},
        "require_biometrics_for_country_change": {"value": True, "description": "Require biometrics when country changes"},
        "require_biometrics_for_high_risk": {"value": True, "description": "Require biometrics for high-risk logins"},
        "enable_device_fingerprinting": {"value": True, "description": "Use composite device fingerprint signals"},
        "enable_trusted_device_cookie_rotation": {"value": True, "description": "Rotate device token after biometric verification"},
        "enable_device_audit": {"value": True, "description": "Record trusted device audit events"},
        "enable_administrator_device_management": {"value": True, "description": "Allow administrators to manage trusted devices"},
        "invalidate_trusted_device_on_logout": {"value": False, "description": "Clear trusted device cookie on logout"},
        "enable_device_trust_levels": {"value": True, "description": "Enable HIGH/MEDIUM/LOW/REVOKED trust levels"},
        "enable_impossible_travel_detection": {"value": True, "description": "Detect implausible geographic login velocity"},
        "enable_device_expiration": {"value": True, "description": "Expire trusted devices after configured duration"},
        "enable_device_notifications": {"value": True, "description": "Send email/SMS/in-app device trust alerts"},
        "enable_device_risk_scores": {"value": True, "description": "Maintain per-device risk scores (0-100)"},
        "enable_high_assurance_indicator": {"value": True, "description": "Expose high assurance session status in UI"},
        "enable_live_session_revocation": {"value": True, "description": "Terminate sessions when device is revoked"},
        "enable_university_device_policies": {"value": True, "description": "Apply separate policies for university-managed devices"},
        "university_device_expiration_days": {"value": 180, "description": "Trust duration for university-managed devices (days)"},
        "personal_device_expiration_days": {"value": 60, "description": "Trust duration for personal devices (days)"},
        "maximum_trust_duration_days": {"value": 180, "description": "Maximum trust duration cap (days)"},
        "maximum_risk_score": {"value": 100, "description": "Maximum device risk score"},
        "impossible_travel_threshold_minutes": {"value": 120, "description": "Minutes between logins to flag impossible travel"},
        "impossible_travel_action": {"value": "REQUIRE_BIOMETRIC", "description": "BLOCK or REQUIRE_BIOMETRIC on impossible travel"},
    },
    "authentication": {
        "jwt_access_minutes": {"value": 15, "description": "JWT access token lifetime (minutes)"},
        "jwt_refresh_days": {"value": 7, "description": "JWT refresh token lifetime (days)"},
        "otp_expiry_minutes": {"value": 10, "description": "OTP expiry (minutes)"},
        "otp_length": {"value": 6, "description": "OTP code length"},
        "max_login_attempts": {"value": 5, "description": "Maximum failed login attempts"},
        "lockout_minutes": {"value": 15, "description": "Account lockout duration (minutes)"},
        "session_timeout_minutes": {"value": 60, "description": "Session inactivity timeout"},
        "remember_me_days": {"value": 7, "description": "Remember me duration (days)"},
        "password_min_length": {"value": 8, "description": "Minimum password length"},
        "mfa_policy": {"value": "super_admin_required", "description": "MFA policy"},
        "super_admin_mfa_required": {"value": True, "description": "Require MFA for Super Admin"},
        "security_key_required": {"value": False, "description": "Require hardware security key"},
    },
    "election_policies": {
        "default_duration_hours": {"value": 24, "description": "Default duration applied when creating new elections (hours)"},
        "default_timezone": {"value": "Africa/Accra", "description": "Default election timezone for new elections"},
        "voting_hours_start": {"value": "08:00", "description": "Legacy default — managed per election by Election Administrators"},
        "voting_hours_end": {"value": "17:00", "description": "Legacy default — managed per election by Election Administrators"},
        "allow_web_voting": {"value": True, "description": "Legacy channel default — configure channels per election"},
        "allow_ussd_voting": {"value": True, "description": "Legacy channel default — configure channels per election"},
        "allow_sms_voting": {"value": False, "description": "Legacy channel default — configure channels per election"},
        "require_svt": {"value": True, "description": "Legacy verification default — managed per election"},
        "require_otp": {"value": True, "description": "Legacy verification default — managed per election"},
        "require_device_verification": {"value": True, "description": "Legacy verification default — managed per election"},
        "require_location_verification": {"value": False, "description": "Legacy verification default — managed per election"},
        "allow_reopening": {"value": False, "description": "Legacy lifecycle default — managed per election"},
        "allow_extensions": {"value": True, "description": "Legacy lifecycle default — managed per election"},
        "max_candidates_per_position": {"value": 20, "description": "Legacy candidate default — managed per election"},
        "turnout_alert_threshold_percent": {"value": 50, "description": "Platform turnout alert threshold (%)"},
    },
    "security": {
        "allowed_domains": {"value": [], "description": "Allowed email domains"},
        "allowed_origins": {"value": ["http://localhost:5173"], "description": "CORS allowed origins", "is_sensitive": True},
        "rate_limit_anon": {"value": "100/hour", "description": "Anonymous rate limit"},
        "rate_limit_user": {"value": "1000/hour", "description": "Authenticated rate limit"},
        "ip_restrictions": {"value": [], "description": "Blocked IP addresses"},
        "trusted_networks": {"value": [], "description": "Trusted network CIDRs"},
        "require_security_key": {"value": False, "description": "Require security key for sensitive actions"},
        "encryption_key_id": {"value": "default", "description": "Active encryption key ID", "is_sensitive": True},
    },
    "api": {
        "rest_enabled": {"value": True, "description": "REST API enabled"},
        "websocket_enabled": {"value": True, "description": "WebSocket enabled"},
        "webhook_urls": {"value": [], "description": "Outbound webhook URLs"},
        "api_version": {"value": "v1", "description": "Active API version"},
        "cors_enabled": {"value": True, "description": "CORS enabled"},
        "health_check_path": {"value": "/health/", "description": "Health check endpoint"},
    },
    "audit": {
        "retention_days": {"value": 365, "description": "Audit log retention (days)"},
        "audit_level": {"value": "standard", "description": "Audit verbosity level"},
        "export_enabled": {"value": True, "description": "Allow audit export"},
        "archive_after_days": {"value": 180, "description": "Archive audit after (days)"},
    },
    "notifications": {
        "queue_limit": {"value": 1000, "description": "Maximum notification queue size"},
        "retry_policy_max": {"value": 3, "description": "Maximum delivery retries"},
        "reminder_schedule_hours": {"value": [24, 2], "description": "Election reminder schedule (hours before)"},
        "election_notifications_enabled": {"value": True, "description": "Election notifications"},
        "result_notifications_enabled": {"value": True, "description": "Result notifications"},
    },
    "runtime": {
        "deployment_mode": {"value": "development" if settings.DEBUG else "production", "description": "Deployment mode", "is_public": True},
        "environment_name": {"value": "development" if settings.DEBUG else "production", "description": "Environment label", "is_public": True},
    },
    "ussd": {
        "ussd_code": {"value": "*920*123#", "description": "USSD short code"},
        "service_name": {"value": "VoteBridge", "description": "USSD service name"},
        "callback_url": {"value": "", "description": "USSD callback URL"},
        "session_timeout_minutes": {"value": 5, "description": "USSD session timeout"},
        "rate_limit_per_msisdn": {"value": 30, "description": "Rate limit per phone number"},
        "voting_enabled": {"value": True, "description": "USSD voting enabled"},
    },
}

DEFAULT_FEATURE_FLAGS = [
    ("fraud_detection", "Fraud Detection", "Enable fraud detection and alerting"),
    ("strongroom", "Strongroom", "Enable strongroom ballot integrity module"),
    ("realtime", "Realtime", "Enable WebSocket realtime updates"),
    ("ussd", "USSD", "Enable USSD voting channel"),
    ("sms", "SMS", "Enable SMS notifications and OTP"),
    ("analytics", "Analytics", "Enable analytics dashboards"),
    ("notifications", "Notifications", "Enable notification centre"),
    ("monitoring", "Monitoring", "Enable operations monitoring"),
    ("future_ai", "Future AI", "Reserved for AI-assisted fraud analysis"),
    ("future_face_verification", "Future Face Verification", "Reserved for face verification"),
    ("future_biometrics", "Future Biometrics", "Reserved for biometric verification"),
]


class SystemAuditService:
    def record(self, user, action: str, *, metadata: dict | None = None, request=None):
        ip = get_client_ip(request) if request else None
        monitoring_service.record_event(
            event_type=AuditLog.EventType.ADMIN_ACTION,
            user=user,
            ip_address=ip,
            metadata={"subsystem": "system_control", "action": action, **(metadata or {})},
        )


class SystemSettingsService:
    def __init__(
        self,
        repository: SystemSettingRepository | None = None,
        revision_repository: SettingRevisionRepository | None = None,
        audit_service: SystemAuditService | None = None,
    ):
        self.repository = repository or SystemSettingRepository()
        self.revision_repository = revision_repository or SettingRevisionRepository()
        self.audit = audit_service or SystemAuditService()

    def ensure_defaults(self):
        for category, keys in DEFAULT_SETTINGS.items():
            for key, meta in keys.items():
                full_key = f"{category}.{key}"
                if self.repository.get_by_key(full_key):
                    continue
                self.repository.create(
                    key=full_key,
                    category=category,
                    value={"value": meta["value"]},
                    description=meta.get("description", ""),
                    is_sensitive=meta.get("is_sensitive", key in SENSITIVE_SETTING_KEYS),
                    is_public=meta.get("is_public", False),
                )

    def get_category(self, category: str) -> list[dict]:
        if category not in SETTING_CATEGORIES:
            raise ValidationError(message=f"Invalid category: {category}", code="invalid_category")
        items = self.repository.list_by_category(category)
        return [self._serialize(s) for s in items]

    def get_public_branding(self) -> dict:
        cached = cache.get("system:public_branding")
        if cached:
            return cached
        institution = InstitutionRepository().get_or_create_profile()
        runtime = {s.key: s.value.get("value") for s in self.repository.list_public()}
        payload = {
            "institution_name": institution.institution_name,
            "short_name": institution.short_name,
            "primary_color": institution.primary_color,
            "secondary_color": institution.secondary_color,
            "logo_url": institution.logo_url or (institution.logo.url if institution.logo else ""),
            "favicon_url": institution.favicon_url or (institution.favicon.url if institution.favicon else ""),
            "branding": institution.branding,
            "runtime": runtime,
        }
        cache.set("system:public_branding", payload, 60)
        return payload

    def update_settings(
        self,
        user,
        category: str,
        updates: dict,
        *,
        step_up_token: str | None = None,
        reason: str = "",
        request=None,
    ) -> list[dict]:
        sensitive = category in {"security", "authentication"} or any(
            k in SENSITIVE_SETTING_KEYS for k in updates
        )
        if sensitive:
            step_up_auth_service.validate_token(user, step_up_token or "")

        results = []
        for key, value in updates.items():
            full_key = key if "." in key else f"{category}.{key}"
            setting = self.repository.get_by_key(full_key)
            if not setting:
                raise NotFoundError(message=f"Setting not found: {full_key}", code="setting_not_found")

            old_value = setting.value
            new_value = {"value": value}
            if setting.is_sensitive and isinstance(value, str) and value and value != "***":
                new_value = {"value": encrypt_secret(value)}

            self.revision_repository.create(
                setting=setting,
                setting_key=setting.key,
                category=setting.category,
                old_value=old_value,
                new_value=new_value,
                version=setting.version + 1,
                changed_by=user,
                change_reason=reason,
            )
            setting.value = new_value
            setting.version += 1
            setting.updated_by = user
            self.repository.save(setting)
            results.append(self._serialize(setting))

        invalidate_settings_cache()
        self.audit.record(
            user,
            "settings_updated",
            metadata={"category": category, "keys": list(updates.keys()), "reason": reason},
            request=request,
        )
        if sensitive and step_up_token:
            step_up_auth_service.consume_token(user, step_up_token)
        return results

    def rollback(self, user, revision_uuid, *, step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        from apps.system.models import SettingRevision

        rev = SettingRevision.objects.filter(uuid=revision_uuid).select_related("setting").first()
        if not rev:
            raise NotFoundError(message="Revision not found.", code="revision_not_found")

        setting = rev.setting
        setting.value = rev.old_value
        setting.version += 1
        setting.updated_by = user
        self.repository.save(setting)
        invalidate_settings_cache()
        self.audit.record(user, "setting_rollback", metadata={"key": setting.key}, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(setting)

    def list_revisions(self, key: str) -> list[dict]:
        return [
            {
                "uuid": str(r.uuid),
                "setting_key": r.setting_key,
                "version": r.version,
                "old_value": r.old_value,
                "new_value": r.new_value,
                "changed_by": r.changed_by.email if r.changed_by else None,
                "change_reason": r.change_reason,
                "created_at": r.created_at.isoformat(),
            }
            for r in SettingRevisionRepository().list_for_key(key)
        ]

    def _serialize(self, setting) -> dict:
        value = setting.value.get("value") if isinstance(setting.value, dict) else setting.value
        display_value = "***" if setting.is_sensitive else value
        return {
            "key": setting.key,
            "category": setting.category,
            "value": display_value,
            "version": setting.version,
            "description": setting.description,
            "is_sensitive": setting.is_sensitive,
            "updated_at": setting.updated_at.isoformat(),
        }


class InstitutionService:
    def __init__(self, repository: InstitutionRepository | None = None, audit: SystemAuditService | None = None):
        self.repository = repository or InstitutionRepository()
        self.audit = audit or SystemAuditService()

    def get_profile(self) -> dict:
        profile = self.repository.get_or_create_profile()
        return self._serialize(profile)

    def update_profile(self, user, data: dict, *, preview: bool = False, request=None) -> dict:
        profile = self.repository.get_or_create_profile()
        if preview:
            merged = self._serialize(profile)
            merged.update({k: v for k, v in data.items() if v is not None})
            return {"preview": merged}

        allowed = {
            "institution_name",
            "short_name",
            "logo_url",
            "favicon_url",
            "primary_color",
            "secondary_color",
            "academic_year",
            "campus",
            "contact_email",
            "contact_phone",
            "election_office_name",
            "election_office_email",
            "election_office_phone",
            "footer_text",
            "public_urls",
            "branding",
        }
        updates = {k: v for k, v in data.items() if k in allowed}
        updates["updated_by"] = user
        self.repository.save_profile(profile, **updates)
        invalidate_settings_cache()
        self.audit.record(user, "institution_updated", metadata={"fields": list(updates.keys())}, request=request)
        return self._serialize(profile)

    def _serialize(self, profile: InstitutionProfile) -> dict:
        return {
            "uuid": str(profile.uuid),
            "institution_name": profile.institution_name,
            "short_name": profile.short_name,
            "logo_url": profile.logo_url or (profile.logo.url if profile.logo else ""),
            "favicon_url": profile.favicon_url or (profile.favicon.url if profile.favicon else ""),
            "primary_color": profile.primary_color,
            "secondary_color": profile.secondary_color,
            "academic_year": profile.academic_year,
            "campus": profile.campus,
            "contact_email": profile.contact_email,
            "contact_phone": profile.contact_phone,
            "election_office_name": profile.election_office_name,
            "election_office_email": profile.election_office_email,
            "election_office_phone": profile.election_office_phone,
            "footer_text": profile.footer_text,
            "public_urls": profile.public_urls,
            "branding": profile.branding,
            "updated_at": profile.updated_at.isoformat(),
        }


class FeatureFlagService:
    def __init__(self, repository: FeatureFlagRepository | None = None, audit: SystemAuditService | None = None):
        self.repository = repository or FeatureFlagRepository()
        self.audit = audit or SystemAuditService()

    def ensure_defaults(self):
        for key, name, description in DEFAULT_FEATURE_FLAGS:
            if self.repository.get_by_key(key):
                continue
            FeatureFlag.objects.create(key=key, name=name, description=description, enabled=True)

    def list_flags(self) -> list[dict]:
        return [self._serialize(f) for f in self.repository.list_all()]

    def is_enabled(self, key: str) -> bool:
        flag = self.repository.get_by_key(key)
        return flag.enabled if flag else True

    def update_flag(self, user, key: str, enabled: bool, *, step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        flag = self.repository.get_by_key(key)
        if not flag:
            raise NotFoundError(message=f"Feature flag not found: {key}", code="flag_not_found")
        flag.enabled = enabled
        flag.last_changed_by = user
        self.repository.save(flag)
        invalidate_settings_cache()
        self.audit.record(user, "feature_flag_toggled", metadata={"key": key, "enabled": enabled}, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(flag)

    def _serialize(self, flag: FeatureFlag) -> dict:
        return {
            "uuid": str(flag.uuid),
            "key": flag.key,
            "name": flag.name,
            "description": flag.description,
            "enabled": flag.enabled,
            "last_changed_by": flag.last_changed_by.email if flag.last_changed_by else None,
            "last_changed_at": flag.last_changed_at.isoformat(),
        }


class MaintenanceService:
    def __init__(self, repository: MaintenanceRepository | None = None, audit: SystemAuditService | None = None):
        self.repository = repository or MaintenanceRepository()
        self.audit = audit or SystemAuditService()

    def get_state(self) -> dict:
        cached = cache.get("system:maintenance")
        if cached:
            return cached
        state = self.repository.get_or_create_state()
        payload = self._serialize(state)
        cache.set("system:maintenance", payload, 30)
        return payload

    def is_maintenance_active(self) -> bool:
        return self.get_state().get("is_enabled", False)

    def update_state(self, user, data: dict, *, step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        state = self.repository.get_or_create_state()
        for field in (
            "is_enabled",
            "read_only_mode",
            "emergency_stop_voting",
            "emergency_stop_results",
            "disable_login",
            "message",
            "expected_return_at",
        ):
            if field in data:
                setattr(state, field, data[field])
        state.updated_by = user
        self.repository.save(state)
        invalidate_settings_cache()
        self.audit.record(user, "maintenance_updated", metadata=data, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(state)

    def _serialize(self, state: MaintenanceState) -> dict:
        return {
            "is_enabled": state.is_enabled,
            "read_only_mode": state.read_only_mode,
            "emergency_stop_voting": state.emergency_stop_voting,
            "emergency_stop_results": state.emergency_stop_results,
            "disable_login": state.disable_login,
            "message": state.message,
            "expected_return_at": state.expected_return_at.isoformat() if state.expected_return_at else None,
            "updated_at": state.updated_at.isoformat(),
        }


class ProviderManagementService:
    def __init__(self, repository: ProviderRepository | None = None, audit: SystemAuditService | None = None):
        self.repository = repository or ProviderRepository()
        self.audit = audit or SystemAuditService()

    def list_providers(self, provider_type: str | None = None) -> list[dict]:
        providers = self.repository.list_all()
        if provider_type:
            providers = [p for p in providers if p.provider_type == provider_type]
        return [self._serialize(p) for p in providers]

    def update_provider(self, user, provider_uuid, data: dict, *, step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        provider = self.repository.get_by_uuid(provider_uuid)
        if not provider:
            raise NotFoundError(message="Provider not found.", code="provider_not_found")

        if "name" in data:
            provider.name = data["name"]
        if "is_active" in data:
            provider.is_active = data["is_active"]
        if "is_default" in data:
            provider.is_default = data["is_default"]
        if "config" in data and isinstance(data["config"], dict):
            merged = dict(provider.config or {})
            for k, v in data["config"].items():
                if v != "***":
                    if k in {"api_key", "password", "secret"} and v:
                        merged[k] = encrypt_secret(v)
                    else:
                        merged[k] = v
            provider.config = merged

        self.repository.save(provider)
        self.audit.record(
            user,
            "provider_updated",
            metadata={"provider_uuid": str(provider_uuid), "type": provider.provider_type},
            request=request,
        )
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(provider)

    def test_provider(self, user, provider_uuid, request=None) -> dict:
        from apps.notifications.repositories.notification_repository import CommunicationProviderRepository

        provider = CommunicationProviderRepository().get_by_uuid(provider_uuid)
        if not provider:
            raise NotFoundError(message="Provider not found.", code="provider_not_found")
        result = communication_service.test_provider(provider_uuid)
        self.audit.record(user, "provider_tested", metadata={"provider_uuid": str(provider_uuid)}, request=request)
        return result

    def _serialize(self, provider) -> dict:
        return {
            "uuid": str(provider.uuid),
            "name": provider.name,
            "provider_type": provider.provider_type,
            "is_active": provider.is_active,
            "is_default": provider.is_default,
            "connection_status": provider.connection_status,
            "last_success_at": provider.last_success_at.isoformat() if provider.last_success_at else None,
            "last_error": provider.last_error,
            "config": mask_config(provider.config),
        }


class StorageService:
    def get_usage(self) -> dict:
        media_root = Path(settings.MEDIA_ROOT)
        log_dir = Path(settings.BASE_DIR) / "logs"
        backup_dir = Path(settings.BASE_DIR) / "backups"

        def dir_size(path: Path) -> int:
            if not path.exists():
                return 0
            return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

        db_size = 0
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_database_size(current_database())"
                )
                db_size = cursor.fetchone()[0]
        except Exception:
            pass

        disk = {}
        if psutil:
            usage = psutil.disk_usage("/")
            disk = {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent,
            }

        return {
            "disk": disk,
            "media_bytes": dir_size(media_root),
            "logs_bytes": dir_size(log_dir),
            "backups_bytes": dir_size(backup_dir),
            "database_bytes": db_size,
            "cache_status": "redis",
            "temporary_bytes": dir_size(Path("/tmp")),
        }

    def cleanup_temp(self, user, *, step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)
        removed = 0
        log_dir = Path(settings.BASE_DIR) / "logs"
        for pattern in ["*.log.1", "*.log.2", "*.log.3", "*.log.4", "*.log.5"]:
            for f in log_dir.glob(pattern):
                f.unlink(missing_ok=True)
                removed += 1
        SystemAuditService().record(user, "storage_cleanup", metadata={"removed_files": removed}, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return {"removed_files": removed}


class BackupService:
    BACKUP_DIR = Path(settings.BASE_DIR) / "backups"

    def __init__(self, repository: BackupRepository | None = None, audit: SystemAuditService | None = None):
        self.repository = repository or BackupRepository()
        self.audit = audit or SystemAuditService()
        self.BACKUP_DIR.mkdir(exist_ok=True)

    def list_backups(self) -> list[dict]:
        return [self._serialize(b) for b in self.repository.list_all()]

    def create_backup(self, user, *, backup_type: str = "manual", step_up_token: str, request=None) -> dict:
        step_up_auth_service.validate_token(user, step_up_token)
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"votebridge_backup_{timestamp}.json"
        filepath = self.BACKUP_DIR / filename

        record = self.repository.create(
            filename=filename,
            file_path=str(filepath),
            status=BackupRecord.Status.RUNNING,
            backup_type=backup_type,
            created_by=user,
        )

        try:
            payload = self._export_config_snapshot()
            filepath.write_text(json.dumps(payload, indent=2, default=str))
            size = filepath.stat().st_size
            record.size_bytes = size
            record.status = BackupRecord.Status.COMPLETED
            self.repository.save(record)
        except Exception as exc:
            record.status = BackupRecord.Status.FAILED
            record.notes = str(exc)
            self.repository.save(record)
            raise

        self.audit.record(user, "backup_created", metadata={"filename": filename}, request=request)
        step_up_auth_service.consume_token(user, step_up_token)
        return self._serialize(record)

    def verify_backup(self, user, backup_uuid, request=None) -> dict:
        record = self.repository.get_by_uuid(backup_uuid)
        if not record or not Path(record.file_path).exists():
            raise NotFoundError(message="Backup not found.", code="backup_not_found")
        json.loads(Path(record.file_path).read_text())
        record.status = BackupRecord.Status.VERIFIED
        record.verified_at = timezone.now()
        self.repository.save(record)
        self.audit.record(user, "backup_verified", metadata={"uuid": str(backup_uuid)}, request=request)
        return self._serialize(record)

    def _export_config_snapshot(self) -> dict:
        settings_svc = SystemSettingsService()
        snapshot = {"exported_at": timezone.now().isoformat(), "settings": {}, "flags": {}}
        for category in SETTING_CATEGORIES:
            snapshot["settings"][category] = settings_svc.get_category(category)
        snapshot["flags"] = FeatureFlagService().list_flags()
        snapshot["institution"] = InstitutionService().get_profile()
        return snapshot

    def _serialize(self, record: BackupRecord) -> dict:
        return {
            "uuid": str(record.uuid),
            "filename": record.filename,
            "size_bytes": record.size_bytes,
            "status": record.status,
            "backup_type": record.backup_type,
            "verified_at": record.verified_at.isoformat() if record.verified_at else None,
            "created_by": record.created_by.email if record.created_by else None,
            "created_at": record.created_at.isoformat(),
            "notes": record.notes,
        }


class EnvironmentService:
    def get_info(self) -> dict:
        uptime_seconds = None
        if psutil:
            uptime_seconds = int(timezone.now().timestamp() - psutil.boot_time())

        pg_version = redis_version = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                pg_version = cursor.fetchone()[0].split(",")[0]
        except Exception:
            pass
        try:
            cache.set("system:env:ping", "1", 5)
            redis_version = "connected"
        except Exception:
            redis_version = "unavailable"

        return {
            "python_version": sys.version.split()[0],
            "django_version": django.get_version(),
            "postgresql_version": pg_version,
            "redis_status": redis_version,
            "operating_system": platform.platform(),
            "cpu_count": os.cpu_count(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2) if psutil else None,
            "disk_gb": round(psutil.disk_usage("/").total / (1024**3), 2) if psutil else None,
            "uptime_seconds": uptime_seconds,
            "deployment_mode": "development" if settings.DEBUG else "production",
        }


PLATFORM_ADMIN_ACTIVITY_LABELS = {
    "backup_created": "Backup created",
    "backup_verified": "Backup verified",
    "maintenance_updated": "Maintenance settings updated",
    "provider_tested": "Communication provider validated",
    "provider_updated": "Communication provider updated",
    "feature_flag_toggled": "Feature flag changed",
    "institution_updated": "Institution profile updated",
    "setting_rollback": "Platform setting rolled back",
    "settings_updated": "Platform defaults updated",
}


class SystemOverviewService:
    def _platform_state(self, has_active_election: bool) -> dict:
        if has_active_election:
            return {
                "primary": "Election in Progress",
                "secondary": "Monitoring Enabled",
                "has_active_election": True,
            }
        return {
            "primary": "No Active Election",
            "secondary": "Platform Ready",
            "has_active_election": False,
        }

    def _admin_activity(self, limit: int = 8) -> list[dict]:
        since = timezone.now() - timedelta(days=14)
        logs = (
            AuditLog.objects.filter(
                event_type=AuditLog.EventType.ADMIN_ACTION,
                timestamp__gte=since,
                election__isnull=True,
            )
            .select_related("user")
            .order_by("-timestamp")[:50]
        )
        activity = []
        for log in logs:
            metadata = log.metadata or {}
            if metadata.get("subsystem") != "system_control":
                continue
            action = metadata.get("action", "")
            title = PLATFORM_ADMIN_ACTIVITY_LABELS.get(action, action.replace("_", " ").title())
            if action == "provider_tested":
                title = "Communication gateway validated"
            elif action == "maintenance_updated" and metadata.get("is_enabled"):
                title = "Maintenance enabled"
            activity.append(
                {
                    "id": log.audit_id,
                    "title": title,
                    "timestamp": log.timestamp.isoformat(),
                    "actor": log.user.get_full_name() if log.user else None,
                }
            )
            if len(activity) >= limit:
                break
        return activity

    def get_overview(self) -> dict:
        health = operations_health_service.check_all()
        comms = communication_service.get_dashboard()
        institution = InstitutionService().get_profile()
        maintenance = MaintenanceService().get_state()
        backups = BackupRepository().list_all(limit=1)
        has_active_election = Election.objects.filter(
            status__in=[Election.Status.OPEN, Election.Status.PAUSED]
        ).exists()
        runtime_setting = SystemSettingRepository().get_by_key("runtime.environment_name")
        env_name = (
            runtime_setting.value.get("value")
            if runtime_setting
            else ("development" if settings.DEBUG else "production")
        )

        components = {c["name"]: c for c in health.get("components", [])}
        sms_providers = [p for p in comms.get("providers", []) if p.get("provider_type") == "sms"]
        email_providers = [p for p in comms.get("providers", []) if p.get("provider_type") == "email"]
        default_sms = sms_providers[0] if sms_providers else {}
        default_email = email_providers[0] if email_providers else {}

        def _iso(value):
            if value is None:
                return None
            return value.isoformat() if hasattr(value, "isoformat") else value

        return {
            "system_status": health.get("overall_status", "unknown"),
            "environment": env_name,
            "application_version": APP_VERSION,
            "release_channel": RELEASE_CHANNEL,
            "build_number": BUILD_NUMBER,
            "database_status": components.get("database", {}).get("status", "unknown"),
            "redis_status": components.get("redis", {}).get("status", "unknown"),
            "websocket_status": components.get("websockets", {}).get("status", "unknown"),
            "sms_provider": default_sms.get("connection_status", "unknown"),
            "email_provider": default_email.get("connection_status", "unknown"),
            "ussd_provider": components.get("ussd", {}).get("status", "unknown"),
            "storage_usage_percent": components.get("storage", {}).get("usage_percent"),
            "last_backup": backups[0].created_at.isoformat() if backups else None,
            "institution": institution.get("institution_name"),
            "platform_state": self._platform_state(has_active_election),
            "maintenance_status": maintenance,
            "system_health": health,
            "admin_activity": self._admin_activity(),
            "integrations": {
                "sms": {
                    "status": default_sms.get("connection_status", "unknown"),
                    "last_sync": _iso(default_sms.get("last_success_at")),
                    "last_error": default_sms.get("last_error"),
                },
                "email": {
                    "status": default_email.get("connection_status", "unknown"),
                    "last_sync": _iso(default_email.get("last_success_at")),
                    "last_error": default_email.get("last_error"),
                },
                "ussd": {
                    "status": components.get("ussd", {}).get("status", "unknown"),
                    "last_sync": components.get("ussd", {}).get("checked_at"),
                    "last_error": components.get("ussd", {}).get("details"),
                },
                "redis": {
                    "status": components.get("redis", {}).get("status", "unknown"),
                    "last_sync": components.get("redis", {}).get("checked_at"),
                    "last_error": components.get("redis", {}).get("details"),
                },
                "websockets": {
                    "status": components.get("websockets", {}).get("status", "unknown"),
                    "last_sync": components.get("websockets", {}).get("checked_at"),
                    "last_error": components.get("websockets", {}).get("details"),
                },
            },
            "quick_actions": [
                {"label": "Enable maintenance", "action": "maintenance_enable", "requires_step_up": True},
                {"label": "Validate SMS gateway", "action": "validate_sms", "requires_step_up": False},
                {"label": "Validate USSD gateway", "action": "validate_ussd", "requires_step_up": False},
                {"label": "Create backup", "action": "create_backup", "requires_step_up": True},
                {"label": "Restore backup", "action": "restore_backup", "requires_step_up": True},
                {"label": "Export system audit", "action": "export_audit", "requires_step_up": False},
                {"label": "Open operations center", "action": "open_operations", "requires_step_up": False},
            ],
        }

    def get_license(self) -> dict:
        institution = InstitutionService().get_profile()
        return {
            "application_version": APP_VERSION,
            "release_channel": RELEASE_CHANNEL,
            "build_number": BUILD_NUMBER,
            "institution_license": f"Enterprise — {institution.get('institution_name')}",
            "support_email": institution.get("election_office_email"),
            "support_phone": institution.get("election_office_phone"),
            "developer": "VoteBridge Engineering",
            "copyright": f"© {datetime.now().year} VoteBridge",
        }


system_settings_service = SystemSettingsService()
institution_service = InstitutionService()
feature_flag_service = FeatureFlagService()
maintenance_service = MaintenanceService()
provider_management_service = ProviderManagementService()
storage_service = StorageService()
backup_service = BackupService()
environment_service = EnvironmentService()
system_overview_service = SystemOverviewService()
step_up_service = step_up_auth_service
