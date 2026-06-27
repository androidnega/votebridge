"""
Base settings shared across all environments.
"""

from datetime import timedelta
from pathlib import Path

import environ

# Build paths: backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    POSTGRES_PORT=(int, 5432),
    REDIS_PORT=(int, 6379),
    REDIS_DB=(int, 0),
    VITE_DEV_MODE=(bool, False),
    VITE_DEV_SERVER_PORT=(int, 5173),
    LOG_LEVEL=(str, "INFO"),
    BIOMETRICS_INFERENCE_MODE=(str, "auto"),
    BIOMETRICS_MODEL_DIR=(str, ""),
)

environ.Env.read_env(PROJECT_ROOT / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "channels",
    "django_vite",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.elections",
    "apps.candidates",
    "apps.voting",
    "apps.security",
    "apps.fraud",
    "apps.results",
    "apps.strongroom",
    "apps.notifications",
    "apps.ussd",
    "apps.dashboard",
    "apps.realtime",
    "apps.operations",
    "apps.system",
    "apps.analytics",
    "apps.biometrics",
    "apps.trusted_devices",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.system.middleware.MaintenanceModeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Custom user model (foundation — extended in Phase 1)
AUTH_USER_MODEL = "accounts.User"

# Database — PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "CONN_MAX_AGE": env.int("POSTGRES_CONN_MAX_AGE", default=60),
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_ROOT / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    PROJECT_ROOT / "frontend" / "dist",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "core.handlers.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login": "5/minute",
        "otp": "3/minute",
        "token_refresh": "30/minute",
        "vote_cast": "20/hour",
        "svt_request": "10/hour",
    },
}

# JWT authentication
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_MINUTES", default=15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "uuid",
    "USER_ID_CLAIM": "user_uuid",
}

# Authentication & MFA
AUTH_SESSION_LIFETIME_DAYS = env.int("AUTH_SESSION_LIFETIME_DAYS", default=7)
OTP_LENGTH = env.int("OTP_LENGTH", default=6)
OTP_EXPIRY_MINUTES = env.int("OTP_EXPIRY_MINUTES", default=10)
OTP_MAX_REQUESTS_PER_WINDOW = env.int("OTP_MAX_REQUESTS_PER_WINDOW", default=5)
OTP_REQUEST_WINDOW_MINUTES = env.int("OTP_REQUEST_WINDOW_MINUTES", default=15)

# Secure Voting Token (SVT)
SVT_EXPIRY_MINUTES = env.int("SVT_EXPIRY_MINUTES", default=30)

# Security alert thresholds
ALERT_LOGIN_ATTEMPTS_WINDOW_MINUTES = env.int("ALERT_LOGIN_ATTEMPTS_WINDOW_MINUTES", default=15)
ALERT_LOGIN_ATTEMPTS_THRESHOLD = env.int("ALERT_LOGIN_ATTEMPTS_THRESHOLD", default=5)
ALERT_SVT_REQUESTS_WINDOW_MINUTES = env.int("ALERT_SVT_REQUESTS_WINDOW_MINUTES", default=60)
ALERT_SVT_REQUESTS_THRESHOLD = env.int("ALERT_SVT_REQUESTS_THRESHOLD", default=5)
ALERT_VOTING_PATTERN_WINDOW_MINUTES = env.int("ALERT_VOTING_PATTERN_WINDOW_MINUTES", default=5)
ALERT_VOTING_PATTERN_THRESHOLD = env.int("ALERT_VOTING_PATTERN_THRESHOLD", default=3)
ALERT_DEVICE_WINDOW_MINUTES = env.int("ALERT_DEVICE_WINDOW_MINUTES", default=1440)
ALERT_LOCATION_WINDOW_MINUTES = env.int("ALERT_LOCATION_WINDOW_MINUTES", default=60)

# Email
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@votebridge.local")

# Arkesel SMS
ARKESEL_API_KEY = env("ARKESEL_API_KEY", default="")
ARKESEL_SENDER_ID = env("ARKESEL_SENDER_ID", default="")
ARKESEL_SMS_URL = env(
    "ARKESEL_SMS_URL",
    default="https://sms.arkesel.com/api/v2/sms/send",
)

# Arkesel USSD
ARKESEL_USSD_USER_ID = env("ARKESEL_USSD_USER_ID", default="VOTEBRIDGE")
ARKESEL_USSD_CALLBACK_SECRET = env("ARKESEL_USSD_CALLBACK_SECRET", default="")
USSD_SESSION_TIMEOUT_MINUTES = env.int("USSD_SESSION_TIMEOUT_MINUTES", default=5)
USSD_RATE_LIMIT_PER_MSISDN = env.int("USSD_RATE_LIMIT_PER_MSISDN", default=30)
USSD_RATE_LIMIT_WINDOW_SECONDS = env.int("USSD_RATE_LIMIT_WINDOW_SECONDS", default=60)

# Django Channels — Redis channel layer
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("CHANNELS_REDIS_URL", default=env("REDIS_URL"))],
        },
    },
}

# Redis cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL"),
    }
}

# Django-Vite integration
DJANGO_VITE = {
    "default": {
        "dev_mode": env("VITE_DEV_MODE"),
        "dev_server_host": env("VITE_DEV_SERVER_HOST", default="localhost"),
        "dev_server_port": env("VITE_DEV_SERVER_PORT"),
        "manifest_path": PROJECT_ROOT / "frontend" / "dist" / "manifest.json",
        "static_url_prefix": "assets",
    }
}

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": env("LOG_LEVEL"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": env("LOG_LEVEL"),
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "votebridge.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "votebridge_errors.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": env("LOG_LEVEL"),
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": env("LOG_LEVEL"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "votebridge": {
            "handlers": ["console", "file", "error_file"],
            "level": env("LOG_LEVEL"),
            "propagate": False,
        },
    },
}

# Biometric identity assurance
BIOMETRICS_INFERENCE_MODE = env("BIOMETRICS_INFERENCE_MODE")
_biometrics_model_dir = env("BIOMETRICS_MODEL_DIR")
BIOMETRICS_MODEL_DIR = Path(_biometrics_model_dir) if _biometrics_model_dir else BASE_DIR / "models" / "biometrics"
