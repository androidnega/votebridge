import logging

from apps.accounts.models import User
from apps.notifications.services.communication_service import communication_service
from apps.trusted_devices.models import TrustedDevice
from apps.trusted_devices.services.policy_service import trusted_device_policy_service

logger = logging.getLogger("votebridge")


class TrustedDeviceNotificationService:
    """Device trust alerts via existing Communication module."""

    def _enabled(self) -> bool:
        return trusted_device_policy_service.get_policy().get("enable_device_notifications", True)

    def _notify(self, user: User, *, subject: str, body: str, metadata: dict | None = None) -> None:
        if not self._enabled() or not user:
            return

        metadata = metadata or {}
        try:
            communication_service.send_raw(
                channel="in_app",
                recipient=str(user.uuid),
                subject=subject,
                body=body,
                user=user,
                metadata={"subsystem": "trusted_devices", **metadata},
            )
        except Exception as exc:
            logger.warning("In-app trusted device notification failed: %s", exc)

        if user.email:
            try:
                communication_service.send_raw(
                    channel="email",
                    recipient=user.email,
                    subject=subject,
                    body=body,
                    user=user,
                    metadata=metadata,
                )
            except Exception as exc:
                logger.warning("Email trusted device notification failed: %s", exc)

        if user.phone_number:
            try:
                communication_service.send_raw(
                    channel="sms",
                    recipient=user.phone_number,
                    subject=subject,
                    body=body[:160],
                    user=user,
                    metadata=metadata,
                )
            except Exception as exc:
                logger.warning("SMS trusted device notification failed: %s", exc)

    def notify_device_registered(self, user: User, device: TrustedDevice) -> None:
        self._notify(
            user,
            subject="New trusted device registered",
            body=f"A new trusted device '{device.device_name}' was registered on your VoteBridge account.",
            metadata={"event": "device_registered", "device_uuid": str(device.uuid)},
        )

    def notify_device_revoked(self, user: User, device: TrustedDevice, *, revoked_by: str = "") -> None:
        self._notify(
            user,
            subject="Trusted device revoked",
            body=f"The trusted device '{device.device_name}' was revoked. Biometric verification is required at next login.",
            metadata={"event": "device_revoked", "device_uuid": str(device.uuid), "revoked_by": revoked_by},
        )

    def notify_high_risk_login(self, user: User, *, risk_score: float, reasons: list[str]) -> None:
        self._notify(
            user,
            subject="High-risk login detected",
            body=f"A high-risk administrator login was detected (score {risk_score:.0f}). Additional verification may be required.",
            metadata={"event": "high_risk_login", "risk_score": risk_score, "reasons": reasons},
        )

    def notify_country_change(self, user: User, *, country: str, city: str) -> None:
        self._notify(
            user,
            subject="Login from new country",
            body=f"A login was attempted from {city or country}. Identity verification may be required.",
            metadata={"event": "country_change", "country": country, "city": city},
        )

    def notify_impossible_travel(self, user: User, *, previous: str, current: str) -> None:
        self._notify(
            user,
            subject="Impossible travel detected",
            body=f"Login blocked or challenged: travel from {previous} to {current} in an implausible timeframe.",
            metadata={"event": "impossible_travel", "previous": previous, "current": current},
        )


trusted_device_notification_service = TrustedDeviceNotificationService()
