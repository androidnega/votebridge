import base64
import json

import numpy as np

from apps.system.utils import decrypt_secret, encrypt_secret
from apps.biometrics.constants import EMBEDDING_DIM


def serialize_embedding(embedding: np.ndarray) -> str:
    """Encrypt embedding vector for storage — never log or expose."""
    payload = json.dumps(embedding.astype(float).tolist())
    return encrypt_secret(payload)


def deserialize_embedding(encrypted: str) -> np.ndarray:
    raw = decrypt_secret(encrypted)
    data = json.loads(raw)
    vec = np.array(data, dtype=np.float32)
    if vec.shape[0] != EMBEDDING_DIM:
        raise ValueError("Invalid embedding dimension.")
    return vec


def decode_image_payload(data: str | bytes) -> bytes:
    if isinstance(data, bytes):
        return data
    if data.startswith("data:"):
        _, encoded = data.split(",", 1)
        return base64.b64decode(encoded)
    return base64.b64decode(data)


def validate_elevation_token(user, *, step_up_token: str | None = None, high_assurance_token: str | None = None) -> str:
    """
    Accept either SCC OTP step-up token or biometric high-assurance token.
    Returns the token type consumed: 'step_up' or 'biometric'.
    """
    from apps.biometrics.services.session_service import biometric_session_service
    from apps.system.services.step_up_service import step_up_auth_service
    from core.exceptions import ValidationError

    if high_assurance_token and str(high_assurance_token).strip():
        biometric_session_service.validate_session(user, str(high_assurance_token).strip())
        return "biometric"
    if step_up_token and str(step_up_token).strip():
        step_up_auth_service.validate_token(user, str(step_up_token).strip())
        return "step_up"
    raise ValidationError(
        message="Step-up or biometric verification is required for this action.",
        code="elevation_required",
    )


def consume_elevation_token(
    user,
    token_type: str,
    *,
    step_up_token: str | None = None,
    high_assurance_token: str | None = None,
) -> None:
    from apps.biometrics.services.session_service import biometric_session_service
    from apps.system.services.step_up_service import step_up_auth_service

    if token_type == "biometric" and high_assurance_token:
        biometric_session_service.consume_session(user, str(high_assurance_token).strip())
    elif token_type == "step_up" and step_up_token:
        step_up_auth_service.consume_token(user, str(step_up_token).strip())
