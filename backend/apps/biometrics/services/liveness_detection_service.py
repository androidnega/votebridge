import logging
import time

from apps.biometrics.inference.engine import inference_engine
from apps.biometrics.services.policy_service import biometric_policy_service
from core.exceptions import ValidationError

logger = logging.getLogger("votebridge")


class LivenessDetectionService:
    """Passive and active liveness detection."""

    def passive_check(self, image_bytes: bytes) -> dict:
        policy = biometric_policy_service.get_policy()
        if not policy.get("enable_passive_liveness", True):
            return {"score": 1.0, "is_live": True, "spoof_type": None, "processing_time_ms": 0}

        threshold = policy.get("liveness_threshold", 0.70)
        result = inference_engine.passive_liveness(image_bytes, threshold=threshold)
        return {
            "score": result.score,
            "is_live": result.is_live,
            "spoof_type": result.spoof_type,
            "processing_time_ms": result.processing_time_ms,
        }

    def evaluate_challenge(
        self,
        challenge_type: str,
        frames: list[bytes],
    ) -> dict:
        policy = biometric_policy_service.get_policy()
        if not policy.get("enable_active_liveness", True):
            return {"passed": True, "reason": "active_liveness_disabled"}

        if not frames:
            raise ValidationError(message="No frames provided for challenge.", code="missing_frames")

        signals = [inference_engine.extract_challenge_signals(frame) for frame in frames]
        if not any(s.face_detected for s in signals):
            return {"passed": False, "reason": "no_face_detected"}

        blink_total = sum(s.blink_count for s in signals)
        max_yaw = max(s.head_yaw for s in signals)
        min_yaw = min(s.head_yaw for s in signals)

        passed = self._check_challenge_type(
            challenge_type,
            blink_total=blink_total,
            max_yaw=max_yaw,
            min_yaw=min_yaw,
            signals=signals,
        )
        return {
            "passed": passed,
            "reason": "challenge_completed" if passed else "challenge_incomplete",
            "blink_total": blink_total,
            "head_yaw_range": [min_yaw, max_yaw],
        }

    @staticmethod
    def _check_challenge_type(
        challenge_type: str,
        *,
        blink_total: int,
        max_yaw: float,
        min_yaw: float,
        signals: list,
    ) -> bool:
        left_turn = max_yaw >= 0.35 or any(s.head_yaw >= 0.35 for s in signals)
        right_turn = min_yaw <= -0.35 or any(s.head_yaw <= -0.35 for s in signals)

        if challenge_type == "blink_once":
            return blink_total >= 1
        if challenge_type == "blink_twice":
            return blink_total >= 2
        if challenge_type == "turn_left":
            return left_turn
        if challenge_type == "turn_right":
            return right_turn
        if challenge_type == "turn_left_then_right":
            return left_turn and right_turn
        if challenge_type == "blink_then_left":
            return blink_total >= 1 and left_turn
        if challenge_type == "blink_then_right":
            return blink_total >= 1 and right_turn
        return False


liveness_detection_service = LivenessDetectionService()
