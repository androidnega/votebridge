"""Biometric ML inference — OpenCV, MediaPipe, InsightFace, MiniFASNet via ONNX Runtime."""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass

import numpy as np
from django.conf import settings
from PIL import Image
from io import BytesIO

logger = logging.getLogger("votebridge")

EMBEDDING_DIM = 512


@dataclass
class FaceAnalysisResult:
    embedding: np.ndarray
    quality_score: float
    face_detected: bool
    liveness_score: float
    is_live: bool
    processing_time_ms: int


@dataclass
class LivenessResult:
    score: float
    is_live: bool
    spoof_type: str | None
    processing_time_ms: int


@dataclass
class ChallengeSignals:
    blink_count: int
    head_yaw: float
    head_pitch: float
    face_detected: bool


class BiometricInferenceEngine:
    """
    Inference wrapper for face detection, liveness, and ArcFace embeddings.

    Uses production ML stack when available; falls back to deterministic mock
    mode for CI and environments without ONNX model files.
    """

    def __init__(self):
        self._mode = getattr(settings, "BIOMETRICS_INFERENCE_MODE", "auto")
        self._cv2 = None
        self._mp_face = None
        self._onnx_session = None
        self._arcface_session = None
        self._initialized = False

    @property
    def mode(self) -> str:
        if self._mode != "auto":
            return self._mode
        try:
            import cv2  # noqa: F401
            import onnxruntime  # noqa: F401

            model_dir = getattr(settings, "BIOMETRICS_MODEL_DIR", None)
            if model_dir:
                return "production"
        except ImportError:
            pass
        return "mock"

    def _ensure_backend(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        if self.mode == "mock":
            return

        try:
            import cv2

            self._cv2 = cv2
        except ImportError:
            logger.warning("OpenCV not available — using mock biometrics inference")
            self._mode = "mock"
            return

        try:
            import mediapipe as mp

            self._mp_face = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
            )
        except ImportError:
            logger.warning("MediaPipe not available — landmark detection limited")

        try:
            import onnxruntime as ort

            model_dir = getattr(settings, "BIOMETRICS_MODEL_DIR", None)
            if model_dir:
                fas_path = model_dir / "mini_fasnet.onnx"
                arc_path = model_dir / "arcface.onnx"
                if fas_path.exists():
                    self._onnx_session = ort.InferenceSession(str(fas_path))
                if arc_path.exists():
                    self._arcface_session = ort.InferenceSession(str(arc_path))
        except ImportError:
            logger.warning("ONNX Runtime not available — using heuristic liveness")

    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        return np.array(img)

    def _mock_embedding(self, image_bytes: bytes) -> np.ndarray:
        digest = hashlib.sha256(image_bytes).digest()
        seed = int.from_bytes(digest[:8], "big") % (2**32 - 1)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
        vec /= np.linalg.norm(vec) + 1e-8
        return vec

    def _mock_liveness(self, image_bytes: bytes) -> float:
        digest = hashlib.sha256(image_bytes).hexdigest()
        return 0.85 + (int(digest[:8], 16) % 1500) / 10000.0

    def _detect_face_opencv(self, rgb: np.ndarray) -> tuple[bool, float]:
        if not self._cv2:
            return True, 0.75
        gray = self._cv2.cvtColor(rgb, self._cv2.COLOR_RGB2GRAY)
        cascade_path = self._cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = self._cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        if len(faces) == 0:
            return False, 0.0
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        area_ratio = (w * h) / (rgb.shape[0] * rgb.shape[1])
        quality = min(1.0, max(0.3, area_ratio * 8))
        return True, quality

    def _run_mini_fasnet(self, rgb: np.ndarray) -> float:
        if not self._onnx_session or not self._cv2:
            return self._mock_liveness(rgb.tobytes())

        resized = self._cv2.resize(rgb, (80, 80))
        tensor = resized.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)
        input_name = self._onnx_session.get_inputs()[0].name
        output = self._onnx_session.run(None, {input_name: tensor})[0]
        probs = self._softmax(output[0])
        return float(probs[1]) if len(probs) > 1 else float(probs[0])

    def _run_arcface(self, rgb: np.ndarray) -> np.ndarray:
        if not self._arcface_session or not self._cv2:
            return self._mock_embedding(rgb.tobytes())

        resized = self._cv2.resize(rgb, (112, 112))
        tensor = resized.astype(np.float32)
        tensor = (tensor - 127.5) / 128.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)
        input_name = self._arcface_session.get_inputs()[0].name
        output = self._arcface_session.run(None, {input_name: tensor})[0][0]
        vec = output.astype(np.float32)
        vec /= np.linalg.norm(vec) + 1e-8
        return vec

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        e = np.exp(x - np.max(x))
        return e / e.sum()

    def analyze_face(self, image_bytes: bytes) -> FaceAnalysisResult:
        start = time.perf_counter()
        if self.mode == "mock":
            liveness = self._mock_liveness(image_bytes)
            elapsed = int((time.perf_counter() - start) * 1000)
            return FaceAnalysisResult(
                embedding=self._mock_embedding(image_bytes),
                quality_score=0.85,
                face_detected=True,
                liveness_score=liveness,
                is_live=liveness >= 0.5,
                processing_time_ms=elapsed,
            )

        self._ensure_backend()
        rgb = self._load_image(image_bytes)

        face_detected, quality = self._detect_face_opencv(rgb)
        embedding = self._run_arcface(rgb) if face_detected else np.zeros(EMBEDDING_DIM, dtype=np.float32)
        liveness = self._run_mini_fasnet(rgb) if face_detected else 0.0

        elapsed = int((time.perf_counter() - start) * 1000)
        return FaceAnalysisResult(
            embedding=embedding,
            quality_score=quality if face_detected else 0.0,
            face_detected=face_detected,
            liveness_score=liveness,
            is_live=liveness >= 0.5,
            processing_time_ms=elapsed,
        )

    def passive_liveness(self, image_bytes: bytes, *, threshold: float = 0.70) -> LivenessResult:
        start = time.perf_counter()
        if self.mode == "mock":
            score = self._mock_liveness(image_bytes)
            elapsed = int((time.perf_counter() - start) * 1000)
            return LivenessResult(
                score=score,
                is_live=score >= threshold,
                spoof_type=None if score >= threshold else "static_face",
                processing_time_ms=elapsed,
            )

        self._ensure_backend()
        rgb = self._load_image(image_bytes)
        face_detected, _ = self._detect_face_opencv(rgb)

        if not face_detected:
            elapsed = int((time.perf_counter() - start) * 1000)
            return LivenessResult(
                score=0.0,
                is_live=False,
                spoof_type="no_face",
                processing_time_ms=elapsed,
            )

        score = self._run_mini_fasnet(rgb)
        spoof = None if score >= threshold else "presentation_attack"

        elapsed = int((time.perf_counter() - start) * 1000)
        return LivenessResult(
            score=score,
            is_live=score >= threshold,
            spoof_type=spoof,
            processing_time_ms=elapsed,
        )

    def extract_challenge_signals(self, image_bytes: bytes) -> ChallengeSignals:
        self._ensure_backend()
        rgb = self._load_image(image_bytes)
        face_detected, _ = self._detect_face_opencv(rgb)

        if self.mode == "mock" or not self._mp_face:
            digest = hashlib.sha256(image_bytes).hexdigest()
            n = int(digest[:4], 16)
            return ChallengeSignals(
                blink_count=n % 3,
                head_yaw=((n % 90) - 45) / 45.0,
                head_pitch=((n % 60) - 30) / 30.0,
                face_detected=face_detected,
            )

        results = self._mp_face.process(rgb)
        if not results.multi_face_landmarks:
            return ChallengeSignals(blink_count=0, head_yaw=0.0, head_pitch=0.0, face_detected=False)

        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = np.mean([(landmarks[i].x, landmarks[i].y) for i in (33, 160, 158, 133, 153, 144)], axis=0)
        right_eye = np.mean([(landmarks[i].x, landmarks[i].y) for i in (362, 385, 387, 263, 373, 380)], axis=0)
        eye_dist = np.linalg.norm(left_eye - right_eye)
        left_open = abs(landmarks[159].y - landmarks[145].y) / (eye_dist + 1e-6)
        right_open = abs(landmarks[386].y - landmarks[374].y) / (eye_dist + 1e-6)
        blink_count = 1 if (left_open + right_open) / 2 < 0.18 else 0

        nose = landmarks[1]
        chin = landmarks[152]
        head_yaw = (nose.x - 0.5) * 2.0
        head_pitch = (chin.y - nose.y - 0.15) * 3.0

        return ChallengeSignals(
            blink_count=blink_count,
            head_yaw=float(head_yaw),
            head_pitch=float(head_pitch),
            face_detected=True,
        )

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        a_norm = a / (np.linalg.norm(a) + 1e-8)
        b_norm = b / (np.linalg.norm(b) + 1e-8)
        return float(np.dot(a_norm, b_norm))

    @staticmethod
    def average_embeddings(embeddings: list[np.ndarray]) -> np.ndarray:
        if not embeddings:
            raise ValueError("No embeddings to average.")
        stacked = np.stack(embeddings, axis=0)
        mean = stacked.mean(axis=0)
        mean /= np.linalg.norm(mean) + 1e-8
        return mean.astype(np.float32)


inference_engine = BiometricInferenceEngine()
