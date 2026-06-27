import logging
import time

import numpy as np
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.biometrics.constants import (
    ENROLLMENT_IMAGE_COUNT,
    ENROLLMENT_MIN_QUALITY,
    ENROLLMENT_POSES,
    MODEL_VERSION,
    EMBEDDING_ALGORITHM,
)
from apps.biometrics.inference.engine import inference_engine
from apps.biometrics.models import BiometricProfile, BiometricVerificationLog
from apps.biometrics.repositories.biometric_repository import BiometricProfileRepository
from apps.biometrics.services.audit_service import biometric_audit_service
from apps.biometrics.services.liveness_detection_service import liveness_detection_service
from apps.biometrics.services.policy_service import biometric_policy_service
from apps.biometrics.validators import decode_image_payload, serialize_embedding
from core.exceptions import PermissionDeniedError, ValidationError

logger = logging.getLogger("votebridge")


class BiometricEnrollmentService:
    """Capture, quality-check, embed, encrypt, and store biometric profiles."""

    def __init__(self, repository: BiometricProfileRepository | None = None):
        self.repository = repository or BiometricProfileRepository()

    def get_enrollment_requirements(self) -> dict:
        return {
            "image_count": ENROLLMENT_IMAGE_COUNT,
            "poses": list(ENROLLMENT_POSES),
            "min_quality": ENROLLMENT_MIN_QUALITY,
        }

    @transaction.atomic
    def enroll(
        self,
        *,
        actor: User,
        target_user: User,
        images: list[str | bytes],
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_fingerprint: str = "",
    ) -> dict:
        if not biometric_policy_service.is_module_enabled():
            raise ValidationError(message="Biometrics module is disabled.", code="biometrics_disabled")

        if not biometric_policy_service.can_enroll_target(actor, target_user):
            raise PermissionDeniedError(
                message="Only Super Admin can enroll privileged users.",
                code="enrollment_forbidden",
            )

        if len(images) < ENROLLMENT_IMAGE_COUNT:
            raise ValidationError(
                message=f"At least {ENROLLMENT_IMAGE_COUNT} images are required.",
                code="insufficient_images",
            )

        embeddings: list[np.ndarray] = []
        quality_scores: list[float] = []
        total_processing_ms = 0

        for idx, raw in enumerate(images[:ENROLLMENT_IMAGE_COUNT]):
            image_bytes = decode_image_payload(raw)
            passive = liveness_detection_service.passive_check(image_bytes)
            if not passive["is_live"]:
                raise ValidationError(
                    message=f"Image {idx + 1} failed liveness check.",
                    code="liveness_failed",
                )

            analysis = inference_engine.analyze_face(image_bytes)
            total_processing_ms += analysis.processing_time_ms

            if not analysis.face_detected:
                raise ValidationError(
                    message=f"No face detected in image {idx + 1}.",
                    code="no_face",
                )
            if analysis.quality_score < ENROLLMENT_MIN_QUALITY:
                raise ValidationError(
                    message=f"Image {idx + 1} quality too low ({analysis.quality_score:.2f}).",
                    code="quality_too_low",
                )
            embeddings.append(analysis.embedding)
            quality_scores.append(analysis.quality_score)

        mean_embedding = inference_engine.average_embeddings(embeddings)
        encrypted = serialize_embedding(mean_embedding)
        avg_quality = sum(quality_scores) / len(quality_scores)

        existing = self.repository.get_by_user(target_user)
        if existing:
            profile = self.repository.update(
                existing,
                encrypted_embedding=encrypted,
                embedding_algorithm=EMBEDDING_ALGORITHM,
                model_version=MODEL_VERSION,
                quality_score=avg_quality,
                enrollment_images_count=len(embeddings),
                is_active=True,
                failed_attempts=0,
                locked_until=None,
            )
        else:
            profile = self.repository.create(
                user=target_user,
                encrypted_embedding=encrypted,
                embedding_algorithm=EMBEDDING_ALGORITHM,
                model_version=MODEL_VERSION,
                quality_score=avg_quality,
                enrollment_images_count=len(embeddings),
                is_active=True,
            )

        biometric_audit_service.record(
            user=target_user,
            event_type=BiometricVerificationLog.EventType.ENROLLMENT,
            outcome=BiometricVerificationLog.Outcome.SUCCESS,
            ip_address=ip_address,
            user_agent=user_agent,
            confidence=avg_quality,
            processing_time_ms=total_processing_ms,
            model_version=MODEL_VERSION,
            device_fingerprint=device_fingerprint,
            metadata={"enrolled_by": str(actor.uuid), "images_count": len(embeddings)},
        )

        return {
            "profile_uuid": str(profile.uuid),
            "user_uuid": str(target_user.uuid),
            "quality_score": avg_quality,
            "enrollment_images_count": len(embeddings),
            "model_version": MODEL_VERSION,
        }


biometric_enrollment_service = BiometricEnrollmentService()
