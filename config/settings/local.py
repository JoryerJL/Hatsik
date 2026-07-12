"""
Local development settings for Hatsik.

Extends base.py with development conveniences.
"""

from .base import *  # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE

# ==============================================================
# Debug
# ==============================================================

DEBUG = True

# ==============================================================
# Debug Toolbar
# ==============================================================

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# ==============================================================
# Static Files (Django built-in serving in dev)
# ==============================================================

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ==============================================================
# Email (console backend for local dev)
# ==============================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
