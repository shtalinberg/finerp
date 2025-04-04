# Django local settings for project.

from .base_dev_local import *

DEBUG = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS += (
    # 'debug_toolbar',
)
