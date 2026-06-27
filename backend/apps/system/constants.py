APP_VERSION = "1.0.0"
RELEASE_CHANNEL = "stable"
BUILD_NUMBER = "2025.06.001"

SETTING_CATEGORIES = frozenset(
    {
        "institution",
        "branding",
        "election_policies",
        "authentication",
        "security",
        "api",
        "audit",
        "notifications",
        "runtime",
        "ussd",
    }
)

SENSITIVE_SETTING_KEYS = frozenset(
    {
        "encryption_key_id",
        "allowed_origins",
        "webhook_secret",
        "api_key_rotation",
    }
)

SENSITIVE_ACTIONS = frozenset(
    {
        "update_provider",
        "rotate_keys",
        "maintenance_enable",
        "backup_restore",
        "update_security",
        "update_authentication",
    }
)

STEP_UP_CACHE_PREFIX = "system:step_up:"
STEP_UP_TTL_SECONDS = 300
