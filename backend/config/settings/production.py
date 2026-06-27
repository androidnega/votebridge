"""
Production settings.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Vite — serve built assets only
DJANGO_VITE["default"]["dev_mode"] = False  # noqa: F405

# Database connection pooling
DATABASES["default"]["CONN_MAX_AGE"] = env.int("POSTGRES_CONN_MAX_AGE", default=300)  # noqa: F405

# Logging — production uses file handlers only for app logs
LOGGING["root"]["handlers"] = ["file"]  # noqa: F405
LOGGING["loggers"]["django"]["handlers"] = ["file", "error_file"]  # noqa: F405
