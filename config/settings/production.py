"""
Production settings for Hatsik.

Extends base.py with security hardening and production services.
"""

from .base import *  # noqa: F401, F403

# ==============================================================
# Security
# ==============================================================

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==============================================================
# Static Files (WhiteNoise — configured in base.py)
# ==============================================================

# WhiteNoise STORAGES already set in base.py
# CompressedManifestStaticFilesStorage handles compression + cache busting
