"""
Development settings.
"""

from config.settings.allowed_hosts import parse_allowed_hosts

from .base import *  # noqa: F401, F403

DEBUG = True

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

# Optional debug toolbar (installed via development requirements)
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass
