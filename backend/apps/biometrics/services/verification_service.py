import logging
import secrets
import time

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services import auth_service, session_service
from apps.biometrics.constants import (
    MODEL_VERSION,
    PENDING_AUTH_CACHE_PREFIX,
    PENDING_AUTH_TTL_SECONDS,
)
from apps.biometrics.inference.engine import inference_engine
from apps.biometrics.models import BiometricProfile, BiometricVerificationLog
from apps.biometrics.repositories.biometric_repository import BiometricProfileRepository
from apps.biometrics.services.audit_service import biometric_audit_service
from apps.biometrics.services.challenge_generator_service import challenge_generator_service
from apps.biometrics.services.liveness_detection_service import liveness_detection_service
from apps.biometrics.services.policy_service import biometric_policy_service
from apps.biometrics.services.session_service import biometric_session_service
from apps.biometrics.validators import decode_image_payload, deserialize_embedding
from core.exceptions import AuthenticationError, PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")


class BiometricVerificationService:
    """Face verification with liveness challenges for privileged access."""

    def __init__(self, repository: BiometricProfileRepository | None = None):
        self.repository = repository or BiometricProfileRepository()

    def resolve_pending_user(self, pending_auth_token: str) -> User:
        return self._resolve_pending_user(pending_auth_token)

    def create_pending_auth(self, user: User, otp_request_uuid: str) -> dict:
        token = secrets.token_urlsafe(32)
        cache_key = f"{PENDING_AUTH_CACHE_PREFIX}{token}"
        cache.set(
            cache_key,
            {"user_uuid": str(user.uuid), "otp_request_uuid": str(otp_request_uuid)},
            PENDING_AUTH_TTL_SECONDS,
        )
        challenge = challenge_generator_service.generate(user)
        return {
            "pending_auth_token": token,
            "requires_biometric": True,
            "challenge": challenge,
            "expires_in_seconds": PENDING_AUTH_TTL_SECONDS,
        }

    def _resolve_pending_user(self, pending_auth_token: str) -> User:
        from apps.accounts.repositories.user_repository import UserRepository

        data = cache.get(f"{PENDING_AUTH_CACHE_PREFIX}{pending_auth_token}")
        if not data:
            raise AuthenticationError(
                message="Biometric authentication session expired. Please sign in again.",
                code="pending_auth_expired",
            )
        user = UserRepository().get_by_uuid(data["user_uuid"])
        if not user:
            raise AuthenticationError(message="User not found.", code="user_not_found")
        return user

    def _consume_pending_auth(self, pending_auth_token: str) -> dict:
        key = f"{PENDING_AUTH_CACHE_PREFIX}{pending_auth_token}"
        data = cache.get(key)
        if data:
            cache.delete(key)
        return data or {}

    def _check_lockout(self, profile: BiometricProfile) -> None:
        if profile.is_locked:
            raise PermissionDeniedError(
                message="Biometric verification locked. Try again later.",
                code="biometric_locked",
            )

    def _handle_failure(
        self,
        profile: BiometricProfile,
        user: User,
        *,
        event_type: str,
        ip_address: str | None,
        user_agent: str | None,
        challenge_type: str = "",
        confidence: float | None = None,
        liveness_score: float | None = None,
        processing_time_ms: int | None = None,
        device_fingerprint: str = "",
        metadata: dict | None = None,
    ) -> None:
        policy = biometric_policy_service.get_policy()
        profile.failed_attempts += 1
        locked = False
        if profile.failed_attempts >= policy.get("maximum_attempts", 5):
            from datetime import timedelta

            profile.locked_until = timezone.now() + timedelta(minutes=policy.get("lockout_minutes", 30))
            profile.failed_attempts = 0
            locked = True
            biometric_audit_service.record(
                user=user,
                event_type=BiometricVerificationLog.EventType.ACCOUNT_LOCKED,
                outcome=BiometricVerificationLog.Outcome.BLOCKED,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
            )
        profile.save()

        biometric_audit_service.record(
            user=user,
            event_type=event_type,
            outcome=BiometricVerificationLog.Outcome.FAILURE,
            ip_address=ip_address,
            user_agent=user_agent,
            challenge_type=challenge_type,
            confidence=confidence,
            liveness_score=liveness_score,
            processing_time_ms=processing_time_ms,
            model_version=MODEL_VERSION,
            device_fingerprint=device_fingerprint,
            metadata={**(metadata or {}), "locked": locked},
        )

    @transaction.atomic
    def verify_login(
        self,
        *,
        pending_auth_token: str,
        challenge_id: str,
        frames: list[str | bytes],
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_fingerprint: str = "",
        device_signals: dict | None = None,
    ) -> dict:
        start = time.perf_counter()
        user = self._resolve_pending_user(pending_auth_token)
        profile = self.repository.get_by_user(user)

        if not profile or not profile.is_active:
            raise ValidationError(
                message="Biometric profile not enrolled. Contact Super Admin.",
                code="not_enrolled",
            )

        self._check_lockout(profile)

        challenge_data = challenge_generator_service.get_challenge(challenge_id)
        if not challenge_data or challenge_data.get("user_uuid") != str(user.uuid):
            raise ValidationError(message="Invalid or expired challenge.", code="invalid_challenge")

        challenge_type = challenge_data["challenge_type"]
        decoded_frames = [decode_image_payload(f) for f in frames]

        policy = biometric_policy_service.get_policy()
        primary_frame = decoded_frames[-1] if decoded_frames else b""
        passive = liveness_detection_service.passive_check(primary_frame)
        if policy.get("enable_passive_liveness") and not passive["is_live"]:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.SPOOF_ATTEMPT,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                liveness_score=passive["score"],
                device_fingerprint=device_fingerprint,
                metadata={"spoof_type": passive.get("spoof_type")},
            )
            raise AuthenticationError(message="Liveness check failed.", code="spoof_detected")

        active = liveness_detection_service.evaluate_challenge(challenge_type, decoded_frames)
        if policy.get("enable_active_liveness") and not active["passed"]:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.CHALLENGE_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="Challenge not completed.", code="challenge_failed")

        analysis = inference_engine.analyze_face(primary_frame)
        if not analysis.face_detected:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.VERIFICATION_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="No face detected.", code="no_face")

        stored = deserialize_embedding(profile.encrypted_embedding)
        confidence = inference_engine.cosine_similarity(stored, analysis.embedding)
        threshold = policy.get("matching_threshold", 0.62)
        matched = confidence >= threshold
        elapsed = int((time.perf_counter() - start) * 1000)

        if not matched:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.VERIFICATION_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                confidence=confidence,
                liveness_score=passive["score"],
                processing_time_ms=elapsed,
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="Face verification failed.", code="face_mismatch")

        challenge_generator_service.consume_challenge(challenge_id)
        self._consume_pending_auth(pending_auth_token)

        profile.failed_attempts = 0
        profile.locked_until = None
        profile.last_verified_at = timezone.now()
        profile.save()

        biometric_audit_service.record(
            user=user,
            event_type=BiometricVerificationLog.EventType.VERIFICATION_PASSED,
            outcome=BiometricVerificationLog.Outcome.SUCCESS,
            ip_address=ip_address,
            user_agent=user_agent,
            challenge_type=challenge_type,
            confidence=confidence if policy.get("enable_confidence_logging") else None,
            liveness_score=passive["score"],
            processing_time_ms=elapsed,
            model_version=MODEL_VERSION,
            device_fingerprint=device_fingerprint,
        )

        session, tokens = session_service.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        ha_session = biometric_session_service.issue_session(user)
        biometric_session_service.register_latest_token(
            user,
            ha_session["high_assurance_token"],
            ha_session["expires_in_seconds"],
        )

        from apps.trusted_devices.services.policy_service import trusted_device_policy_service
        from apps.trusted_devices.services.registration_service import trusted_device_registration_service
        from apps.trusted_devices.utils import build_device_context

        policy = trusted_device_policy_service.get_policy()
        raw_device_token = ""
        device_registered = False
        if policy.get("enable_trusted_devices"):
            context = build_device_context(
                user_agent=user_agent or "",
                browser_fingerprint=device_fingerprint,
                signals=device_signals,
            )
            raw_device_token, registered_device = trusted_device_registration_service.register_after_biometric(
                user,
                context,
                ip_address=ip_address,
            )
            device_registered = registered_device is not None

        return {
            "user_uuid": str(user.uuid),
            "session_uuid": str(session.uuid),
            "tokens": tokens,
            "redirect_path": auth_service.dashboard_path_for_role(user.role.name),
            "verification": {
                "matched": True,
                "confidence": confidence,
                "processing_time_ms": elapsed,
            },
            "high_assurance": ha_session,
            "device_registered": device_registered,
            "_trusted_device_token": raw_device_token,
            "_cookie_max_age_seconds": policy.get("trusted_device_expiration_days", 90) * 86400,
        }

    def verify_step_up(
        self,
        *,
        user: User,
        challenge_id: str,
        frames: list[str | bytes],
        action: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_fingerprint: str = "",
    ) -> dict:
        if not biometric_policy_service.requires_step_up(user, action):
            raise ValidationError(message="Step-up not required for this action.", code="step_up_not_required")

        profile = self.repository.get_by_user(user)
        if not profile or not profile.is_active:
            raise ValidationError(message="Biometric profile not enrolled.", code="not_enrolled")

        self._check_lockout(profile)

        challenge_data = challenge_generator_service.get_challenge(challenge_id)
        if not challenge_data or challenge_data.get("user_uuid") != str(user.uuid):
            raise ValidationError(message="Invalid or expired challenge.", code="invalid_challenge")

        challenge_type = challenge_data["challenge_type"]
        decoded_frames = [decode_image_payload(f) for f in frames]
        primary_frame = decoded_frames[-1] if decoded_frames else b""

        policy = biometric_policy_service.get_policy()
        passive = liveness_detection_service.passive_check(primary_frame)
        if policy.get("enable_passive_liveness") and not passive["is_live"]:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.SPOOF_ATTEMPT,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                liveness_score=passive["score"],
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="Liveness check failed.", code="spoof_detected")

        active = liveness_detection_service.evaluate_challenge(challenge_type, decoded_frames)
        if policy.get("enable_active_liveness") and not active["passed"]:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.CHALLENGE_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="Challenge not completed.", code="challenge_failed")

        analysis = inference_engine.analyze_face(primary_frame)
        stored = deserialize_embedding(profile.encrypted_embedding)
        confidence = inference_engine.cosine_similarity(stored, analysis.embedding)
        threshold = policy.get("matching_threshold", 0.62)

        if confidence < threshold:
            self._handle_failure(
                profile,
                user,
                event_type=BiometricVerificationLog.EventType.VERIFICATION_FAILED,
                ip_address=ip_address,
                user_agent=user_agent,
                challenge_type=challenge_type,
                confidence=confidence,
                device_fingerprint=device_fingerprint,
            )
            raise AuthenticationError(message="Face verification failed.", code="face_mismatch")

        challenge_generator_service.consume_challenge(challenge_id)
        profile.last_verified_at = timezone.now()
        profile.failed_attempts = 0
        profile.save()

        event_type = (
            BiometricVerificationLog.EventType.STRONGROOM_VERIFICATION
            if action == "strongroom_access"
            else BiometricVerificationLog.EventType.STEP_UP
        )
        biometric_audit_service.record(
            user=user,
            event_type=event_type,
            outcome=BiometricVerificationLog.Outcome.SUCCESS,
            ip_address=ip_address,
            user_agent=user_agent,
            challenge_type=challenge_type,
            confidence=confidence,
            device_fingerprint=device_fingerprint,
            metadata={"action": action},
        )

        ha_session = biometric_session_service.issue_session(user)
        biometric_session_service.register_latest_token(
            user,
            ha_session["high_assurance_token"],
            ha_session["expires_in_seconds"],
        )
        return {
            "high_assurance_token": ha_session["high_assurance_token"],
            "expires_in_seconds": ha_session["expires_in_seconds"],
            "verification": {
                "matched": True,
                "confidence": confidence,
            },
        }

    def get_status(self, user: User) -> dict:
        profile = self.repository.get_by_user(user)
        policy = biometric_policy_service.get_policy()
        privileged = biometric_audit_service.is_privileged_user(user)
        return {
            "module_enabled": policy.get("enabled", False),
            "required_for_user": privileged and policy.get("enable_face_verification", False),
            "enrolled": bool(profile and profile.is_active),
            "is_locked": bool(profile and profile.is_locked),
            "last_verified_at": profile.last_verified_at if profile else None,
            "quality_score": profile.quality_score if profile else None,
            "model_version": profile.model_version if profile else None,
            "failed_attempts": profile.failed_attempts if profile else 0,
        }


biometric_verification_service = BiometricVerificationService()
