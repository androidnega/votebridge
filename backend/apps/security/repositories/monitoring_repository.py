from django.db.models import Count, QuerySet
from django.utils import timezone

from apps.security.models import AuditLog, DeviceLog, LocationLog


class AuditLogRepository:
    def get_queryset(self) -> QuerySet[AuditLog]:
        return AuditLog.objects.select_related(
            "user",
            "election",
            "device_log",
            "location_log",
        ).all()

    def create(self, **data) -> AuditLog:
        return AuditLog.objects.create(**data)

    def list_recent(self, limit: int = 100):
        return self.get_queryset()[:limit]

    def list_filtered(
        self,
        event_type: str | None = None,
        election_id: int | None = None,
        user_id: int | None = None,
        since=None,
    ):
        qs = self.get_queryset()
        if event_type:
            qs = qs.filter(event_type=event_type)
        if election_id:
            qs = qs.filter(election_id=election_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if since:
            qs = qs.filter(timestamp__gte=since)
        return qs

    def count_events(self, event_type: str, since, user_id=None, ip_address=None) -> int:
        qs = AuditLog.objects.filter(event_type=event_type, timestamp__gte=since)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if ip_address:
            qs = qs.filter(ip_address=ip_address)
        return qs.count()


class DeviceLogRepository:
    def get_queryset(self) -> QuerySet[DeviceLog]:
        return DeviceLog.objects.select_related("user").all()

    def get_by_fingerprint_and_user(self, fingerprint: str, user_id: int | None):
        return self.get_queryset().filter(
            browser_fingerprint=fingerprint,
            user_id=user_id,
        ).first()

    def upsert(self, fingerprint: str, user, user_agent: str, device_type: str, operating_system: str) -> DeviceLog:
        now = timezone.now()
        device = self.get_queryset().filter(
            browser_fingerprint=fingerprint,
            user_id=user.id if user else None,
        ).first()
        if device:
            device.user_agent = user_agent
            device.device_type = device_type
            device.operating_system = operating_system
            device.last_seen_at = now
            device.save(update_fields=["user_agent", "device_type", "operating_system", "last_seen_at"])
            return device
        return DeviceLog.objects.create(
            user=user,
            browser_fingerprint=fingerprint,
            device_type=device_type,
            operating_system=operating_system,
            user_agent=user_agent,
            last_seen_at=now,
        )

    def list_distinct_users_for_fingerprint(self, fingerprint: str, since):
        return (
            self.get_queryset()
            .filter(browser_fingerprint=fingerprint, last_seen_at__gte=since)
            .exclude(user_id__isnull=True)
            .values("user_id")
            .distinct()
        )

    def count_users_for_fingerprint(self, fingerprint: str, since) -> int:
        return self.list_distinct_users_for_fingerprint(fingerprint, since).count()


class LocationLogRepository:
    def get_queryset(self) -> QuerySet[LocationLog]:
        return LocationLog.objects.all()

    def get_by_ip(self, ip_address: str) -> LocationLog | None:
        return self.get_queryset().filter(ip_address=ip_address).first()

    def upsert(self, ip_address: str, geo: dict) -> LocationLog:
        now = timezone.now()
        location = self.get_by_ip(ip_address)
        if location:
            location.country = geo.get("country", location.country)
            location.region = geo.get("region", location.region)
            location.city = geo.get("city", location.city)
            location.latitude = geo.get("latitude", location.latitude)
            location.longitude = geo.get("longitude", location.longitude)
            location.last_seen_at = now
            location.save()
            return location
        return LocationLog.objects.create(
            ip_address=ip_address,
            country=geo.get("country", ""),
            region=geo.get("region", ""),
            city=geo.get("city", ""),
            latitude=geo.get("latitude"),
            longitude=geo.get("longitude"),
            last_seen_at=now,
        )

    def count_users_for_ip(self, ip_address: str, since) -> int:
        return (
            AuditLog.objects.filter(ip_address=ip_address, timestamp__gte=since)
            .exclude(user_id__isnull=True)
            .values("user_id")
            .distinct()
            .count()
        )
