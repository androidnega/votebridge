"""Development-only full reset and bootstrap — clears demo data, preserves platform config."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from apps.accounts.models import MFALog, OTPRequest, Role, Session
from apps.accounts.utils.phone import normalize_phone
from apps.biometrics.models import BiometricProfile, BiometricVerificationLog
from apps.elections.services.election_purge_service import election_purge_service
from apps.notifications.models import CommunicationProvider, DeliveryLog, InAppNotification, NotificationTemplate
from apps.security.models import AuditLog, DeviceLog, LocationLog
from apps.system.models import (
    BackupRecord,
    FeatureFlag,
    InstitutionProfile,
    MaintenanceState,
    SystemSetting,
)
from apps.trusted_devices.models import (
    TrustedDevice,
    TrustedDeviceEvent,
    TrustedDeviceLoginHistory,
)
from apps.ussd.models import USSDRequestLog, USSDSession
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")

User = get_user_model()

DEV_RESET_CONFIRMATION = "RESET VOTEBRIDGE DEV"

BOOTSTRAP_SUPER_ADMIN = {
    "username": "superadmin",
    "email": "superadmin@votebridge.local",
    "password": "[REDACTED]",
    "phone_number": "0257940791",
    "first_name": "Super",
    "last_name": "Admin",
    "role": Role.Name.SUPER_ADMIN,
    "is_staff": True,
    "is_superuser": True,
}

BOOTSTRAP_ELECTION_ADMIN = {
    "username": "admin",
    "email": "admin@votebridge.local",
    "password": "[REDACTED]",
    "phone_number": "0257940792",
    "first_name": "Election",
    "last_name": "Admin",
    "role": Role.Name.ADMIN,
    "is_staff": True,
    "is_superuser": False,
}

PRESERVED_MODEL_LABELS = [
    "Role",
    "InstitutionProfile",
    "SystemSetting",
    "SettingRevision",
    "FeatureFlag",
    "MaintenanceState",
    "BackupRecord",
    "CommunicationProvider",
    "NotificationTemplate",
]


@dataclass
class DevResetSummary:
    cleared: dict[str, int] = field(default_factory=dict)
    preserved: list[str] = field(default_factory=lambda: list(PRESERVED_MODEL_LABELS))
    users_created: list[dict] = field(default_factory=list)
    dev_otp_fallback_enabled: bool = False

    def as_dict(self) -> dict:
        return {
            "cleared": self.cleared,
            "preserved": self.preserved,
            "users_created": self.users_created,
            "dev_otp_fallback_enabled": self.dev_otp_fallback_enabled,
        }


class DevResetService:
    """Wipe demo operational and user data; bootstrap fresh dev accounts."""

    def assert_dev_environment(self) -> None:
        if settings.DEBUG is not True:
            raise ValidationError(
                message="Development reset is only allowed when DEBUG=True.",
                code="dev_reset_disabled",
            )

    @transaction.atomic
    def reset_and_bootstrap(self) -> DevResetSummary:
        self.assert_dev_environment()
        summary = DevResetSummary()

        operational = election_purge_service.reset_all_operational_data()
        summary.cleared["elections"] = operational.elections_removed
        summary.cleared["votes"] = operational.votes_removed
        summary.cleared["results"] = operational.results_removed

        summary.cleared["in_app_notifications"] = self._delete_count(InAppNotification.objects.all())
        summary.cleared["delivery_logs"] = self._delete_count(DeliveryLog.objects.all())
        summary.cleared["ussd_sessions"] = self._delete_count(USSDSession.objects.all())
        summary.cleared["ussd_request_logs"] = self._delete_count(USSDRequestLog.objects.all())

        summary.cleared["trusted_device_login_history"] = self._delete_count(
            TrustedDeviceLoginHistory.objects.all()
        )
        summary.cleared["trusted_device_events"] = self._delete_count(TrustedDeviceEvent.objects.all())
        summary.cleared["trusted_devices"] = self._delete_count(TrustedDevice.objects.all())

        summary.cleared["biometric_verification_logs"] = self._delete_count(
            BiometricVerificationLog.objects.all()
        )
        summary.cleared["biometric_profiles"] = self._delete_count(BiometricProfile.objects.all())

        summary.cleared["otp_requests"] = self._delete_count(OTPRequest.objects.all())
        summary.cleared["auth_sessions"] = self._delete_count(Session.objects.all())
        summary.cleared["mfa_logs"] = self._delete_count(MFALog.objects.all())

        summary.cleared["device_logs"] = self._delete_count(DeviceLog.objects.all())
        summary.cleared["location_logs"] = self._delete_count(LocationLog.objects.all())
        summary.cleared["audit_logs"] = self._delete_count(AuditLog.objects.all())

        summary.cleared["users"] = self._delete_count(User.objects.all())

        cache.delete("analytics:overview")
        cache.delete("operations:overview")

        summary.users_created = self._bootstrap_users()
        summary.dev_otp_fallback_enabled = bool(
            getattr(settings, "DEV_OTP_FALLBACK_ENABLED", False) and settings.DEBUG
        )

        self._record_preserved_counts(summary)
        logger.warning(
            "VoteBridge development reset completed — %s users created",
            len(summary.users_created),
        )
        return summary

    def _delete_count(self, queryset) -> int:
        count, _ = queryset.delete()
        return count

    def _bootstrap_users(self) -> list[dict]:
        created = []
        for spec in (BOOTSTRAP_SUPER_ADMIN, BOOTSTRAP_ELECTION_ADMIN):
            role = Role.objects.filter(name=spec["role"]).first()
            if not role:
                raise ValidationError(
                    message=f"Role '{spec['role']}' not found. Run migrations first.",
                    code="role_missing",
                )

            phone = normalize_phone(spec.get("phone_number", ""))
            user = User.objects.create_user(
                email=spec["email"],
                password=spec["password"],
                username=spec["username"],
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                role=role,
                phone_number=phone or spec.get("phone_number", ""),
                is_verified=True,
                is_staff=spec.get("is_staff", False),
                is_superuser=spec.get("is_superuser", False),
                is_active=True,
            )
            created.append(
                {
                    "username": user.username,
                    "email": user.email,
                    "role": role.name,
                    "phone_number": user.phone_number,
                }
            )
        return created

    def _record_preserved_counts(self, summary: DevResetSummary) -> None:
        summary.preserved = [
            f"Role ({Role.objects.count()} rows)",
            f"InstitutionProfile ({InstitutionProfile.objects.count()} rows)",
            f"SystemSetting ({SystemSetting.objects.count()} rows)",
            f"FeatureFlag ({FeatureFlag.objects.count()} rows)",
            f"MaintenanceState ({MaintenanceState.objects.count()} rows)",
            f"BackupRecord ({BackupRecord.objects.count()} rows)",
            f"CommunicationProvider ({CommunicationProvider.objects.count()} rows)",
            f"NotificationTemplate ({NotificationTemplate.objects.count()} rows)",
        ]


dev_reset_service = DevResetService()
