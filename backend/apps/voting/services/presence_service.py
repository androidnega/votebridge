import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MFALog
from apps.accounts.services.mfa_service import MFAService
from apps.elections.repositories.election_repository import ElectionRepository
from apps.security.models import SVTToken
from apps.security.repositories.svt_repository import SVTRepository
from apps.security.services.svt_service import SVTService
from apps.voting.models import PreVotePresenceCapture
from apps.voting.repositories.presence_repository import PreVotePresenceRepository
from core.exceptions import NotFoundError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


class PreVotePresenceService:
    """Stores web pre-vote human presence evidence linked to ballot sessions."""

    def __init__(
        self,
        presence_repository: PreVotePresenceRepository | None = None,
        election_repository: ElectionRepository | None = None,
        svt_repository: SVTRepository | None = None,
        svt_service: SVTService | None = None,
        mfa_service: MFAService | None = None,
    ):
        self.presence_repository = presence_repository or PreVotePresenceRepository()
        self.election_repository = election_repository or ElectionRepository()
        self.svt_repository = svt_repository or SVTRepository()
        self.svt_service = svt_service or SVTService()
        self.mfa_service = mfa_service or MFAService()

    def get_status(self, election_uuid, user) -> dict:
        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        active_svt = self.svt_repository.get_active_svt_for_user_election(user, election)
        if not active_svt or active_svt.status != SVTToken.Status.VALIDATED:
            return {
                "election_uuid": str(election.uuid),
                "election_title": election.title,
                "presence_required": False,
                "presence_captured": False,
                "captured_at": None,
                "svt_id": str(active_svt.svt_id) if active_svt else None,
            }

        capture = self.presence_repository.get_for_svt(active_svt.svt_id)
        return {
            "election_uuid": str(election.uuid),
            "election_title": election.title,
            "presence_required": True,
            "presence_captured": capture is not None,
            "captured_at": capture.captured_at if capture else None,
            "svt_id": str(active_svt.svt_id),
        }

    def has_capture_for_svt(self, svt_id) -> bool:
        return self.presence_repository.get_for_svt(svt_id) is not None

    def ensure_presence_for_web_ballot(self, user, election, svt: SVTToken) -> None:
        if svt.status != SVTToken.Status.VALIDATED:
            return
        if self.has_capture_for_svt(svt.svt_id):
            return
        raise PermissionDeniedError(
            message="Complete presence verification before opening your ballot.",
            code="presence_required",
        )

    @transaction.atomic
    def submit_capture(
        self,
        election_uuid,
        user,
        token_code: str,
        image,
        channel: str = PreVotePresenceCapture.Channel.WEB,
        ip_address=None,
        user_agent=None,
    ) -> dict:
        if channel != PreVotePresenceCapture.Channel.WEB:
            raise ValidationError(
                message="Presence capture is only supported for web voting.",
                code="invalid_channel",
            )

        election = self.election_repository.get_by_uuid(election_uuid)
        if not election:
            raise NotFoundError(message="Election not found.", code="election_not_found")

        svt = self.svt_service.get_svt_for_submit(token_code, user, election_uuid)
        if svt.status != SVTToken.Status.VALIDATED:
            raise ValidationError(
                message="Your ballot session is not ready for presence capture.",
                code="invalid_svt_status",
            )

        existing = self.presence_repository.get_for_user_election_svt(
            user, election, svt.svt_id
        )
        if existing:
            return self._serialize_capture(existing)

        self._validate_image(image)
        captured_at = timezone.now()
        capture = self.presence_repository.create(
            user=user,
            election=election,
            svt_id=svt.svt_id,
            channel=channel,
            image=image,
            captured_at=captured_at,
        )

        self.mfa_service.log(
            event_type=MFALog.EventType.PRE_VOTE_PRESENCE_CAPTURED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "election_uuid": str(election.uuid),
                "svt_id": str(svt.svt_id),
                "channel": channel,
                "capture_uuid": str(capture.uuid),
            },
        )
        logger.info(
            "Pre-vote presence captured: %s for user %s election %s",
            capture.uuid,
            user.uuid,
            election.uuid,
        )
        return self._serialize_capture(capture)

    def _validate_image(self, image) -> None:
        if not image:
            raise ValidationError(message="A photo is required.", code="image_required")

        content_type = getattr(image, "content_type", "") or ""
        if content_type.lower() not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                message="Upload a JPEG or PNG photo.",
                code="invalid_image_type",
            )

        size = getattr(image, "size", 0) or 0
        if size <= 0:
            raise ValidationError(message="The photo file is empty.", code="empty_image")
        if size > MAX_IMAGE_BYTES:
            raise ValidationError(
                message="Photo is too large. Maximum size is 5 MB.",
                code="image_too_large",
            )

    @staticmethod
    def _serialize_capture(capture: PreVotePresenceCapture) -> dict:
        return {
            "uuid": str(capture.uuid),
            "election_uuid": str(capture.election.uuid),
            "election_title": capture.election.title,
            "svt_id": str(capture.svt_id),
            "channel": capture.channel,
            "captured_at": capture.captured_at,
            "message": "Presence photo saved successfully.",
        }


pre_vote_presence_service = PreVotePresenceService()
