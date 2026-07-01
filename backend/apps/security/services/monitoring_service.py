import hashlib
import ipaddress
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.elections.repositories.election_repository import ElectionRepository
from apps.fraud.models import SecurityAlert
from apps.fraud.repositories.alert_repository import SecurityAlertRepository
from apps.fraud.services.alert_detection_service import AlertDetectionService
from apps.security.models import AuditLog, DeviceLog, LocationLog, parse_device_type, parse_operating_system
from apps.trusted_devices.utils import normalize_browser_fingerprint
from apps.security.repositories.monitoring_repository import (
    AuditLogRepository,
    DeviceLogRepository,
    LocationLogRepository,
)

logger = logging.getLogger("votebridge")


def resolve_ip_geolocation(ip_address: str) -> dict:
    if not ip_address:
        return {
            "country": "Unknown",
            "region": "",
            "city": "",
            "latitude": None,
            "longitude": None,
        }
    try:
        ip_obj = ipaddress.ip_address(ip_address)
        if ip_obj.is_loopback:
            return {"country": "Local", "region": "Loopback", "city": "Local", "latitude": None, "longitude": None}
        if ip_obj.is_private:
            return {"country": "Private", "region": "Private Network", "city": "", "latitude": None, "longitude": None}
    except ValueError:
        pass
    return {"country": "Unknown", "region": "", "city": "", "latitude": None, "longitude": None}


class MonitoringService:
    """Central facade for audit logging, device/location tracking, and alert detection."""

    def __init__(
        self,
        audit_repository: AuditLogRepository | None = None,
        device_repository: DeviceLogRepository | None = None,
        location_repository: LocationLogRepository | None = None,
        election_repository: ElectionRepository | None = None,
        alert_detection: AlertDetectionService | None = None,
    ):
        self.audit_repository = audit_repository or AuditLogRepository()
        self.device_repository = device_repository or DeviceLogRepository()
        self.location_repository = location_repository or LocationLogRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.alert_detection = alert_detection or AlertDetectionService()

    def record_event(
        self,
        event_type: str,
        user=None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        browser_fingerprint: str | None = None,
        metadata: dict | None = None,
        election_uuid: str | None = None,
    ) -> AuditLog:
        metadata = metadata or {}
        user_agent = user_agent or ""

        if not browser_fingerprint and user_agent:
            browser_fingerprint = hashlib.sha256(user_agent.encode("utf-8")).hexdigest()
        else:
            browser_fingerprint = normalize_browser_fingerprint(browser_fingerprint)

        device_log = None
        if browser_fingerprint:
            device_log = self.device_repository.upsert(
                fingerprint=browser_fingerprint,
                user=user,
                user_agent=user_agent,
                device_type=parse_device_type(user_agent),
                operating_system=parse_operating_system(user_agent),
            )

        location_log = None
        if ip_address:
            geo = resolve_ip_geolocation(ip_address)
            location_log = self.location_repository.upsert(ip_address, geo)

        election = None
        election_uuid = election_uuid or metadata.get("election_uuid")
        if election_uuid:
            election = self.election_repository.get_by_uuid(election_uuid)

        audit_log = self.audit_repository.create(
            user=user,
            election=election,
            device_log=device_log,
            location_log=location_log,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
            timestamp=timezone.now(),
        )

        try:
            self.alert_detection.evaluate(
                audit_log=audit_log,
                device_log=device_log,
                location_log=location_log,
            )
        except Exception:
            logger.exception("Alert detection failed for event %s", event_type)

        return audit_log


monitoring_service = MonitoringService()
