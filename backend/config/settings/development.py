"""
Development settings.
"""

from config.settings.allowed_hosts import parse_allowed_hosts

from .base import *  # noqa: F401, F403

DEBUG = True

# Override Django's WSGI runserver with core's uvicorn-based ASGI runserver.
INSTALLED_APPS = ["core"] + INSTALLED_APPS  # noqa: F405

ALLOWED_HOSTS = parse_allowed_hosts(
    env("DJANGO_ALLOWED_HOSTS"),  # noqa: F405
    debug=True,
    include_local_defaults=True,
)

# Allow JSON browsable API in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Vite dev server
DJANGO_VITE["default"]["dev_mode"] = True  # noqa: F405

# Static files — skip manifest requirement in development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Email — console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# In-memory cache for dev — avoids Redis connection churn from DRF throttling and
# debug toolbar, which can exhaust macOS soft file-descriptor limits on long runs.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "votebridge-dev",
    }
}

# Relaxed auth limits for local development and demo flows.
OTP_MAX_REQUESTS_PER_WINDOW = 20
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "30/minute"  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["otp"] = "20/minute"  # noqa: F405

# Dev OTP/SVT fallbacks: configure via .env (see .env.example). Never hardcode secrets here.

# Close DB connections after each request in dev — prevents idle pool buildup from
# runserver autoreload and long sessions exhausting local Postgres slots.
DATABASES["default"]["CONN_MAX_AGE"] = 0  # noqa: F405

# Optional debug toolbar (installed via development requirements)
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass
