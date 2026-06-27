"""Biometric identity assurance constants."""

from apps.accounts.models import Role

PRIVILEGED_ROLES = frozenset({Role.Name.ADMIN, Role.Name.SUPER_ADMIN})

PRIVILEGED_USERNAMES = frozenset({"registrar", "electionofficer", "admin"})

ENROLLMENT_IMAGE_COUNT = 10
ENROLLMENT_MIN_QUALITY = 0.55
EMBEDDING_ALGORITHM = "arcface"
MODEL_VERSION = "arcface_v1"
EMBEDDING_DIM = 512

DEFAULT_MATCH_THRESHOLD = 0.62
DEFAULT_LIVENESS_THRESHOLD = 0.70
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_LOCKOUT_MINUTES = 30
DEFAULT_SESSION_TIMEOUT_MINUTES = 15

HIGH_ASSURANCE_CACHE_PREFIX = "biometrics:ha_session:"
PENDING_AUTH_CACHE_PREFIX = "biometrics:pending_auth:"
CHALLENGE_CACHE_PREFIX = "biometrics:challenge:"

PENDING_AUTH_TTL_SECONDS = 600
CHALLENGE_TTL_SECONDS = 300

CHALLENGE_TYPES = (
    "blink_once",
    "blink_twice",
    "turn_left",
    "turn_right",
    "turn_left_then_right",
    "blink_then_left",
    "blink_then_right",
)

CHALLENGE_LABELS = {
    "blink_once": "Blink once",
    "blink_twice": "Blink twice",
    "turn_left": "Turn your head left",
    "turn_right": "Turn your head right",
    "turn_left_then_right": "Turn left, then right",
    "blink_then_left": "Blink, then turn left",
    "blink_then_right": "Blink, then turn right",
}

ENROLLMENT_POSES = (
    "look_forward",
    "blink",
    "turn_left",
    "turn_right",
)

STEP_UP_ACTIONS = frozenset(
    {
        "strongroom_access",
        "result_certification",
        "election_deletion",
        "api_key_change",
        "jwt_secret_change",
        "sms_provider_change",
        "ussd_provider_change",
        "system_control_access",
    }
)
