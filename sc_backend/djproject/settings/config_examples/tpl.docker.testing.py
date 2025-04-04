import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from djproject.settings.testing import *


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError as err:
        raise ImproperlyConfigured(
            f" Problem with set the {env_variable} environment variable: {err}"
        )


# Database
DATABASES["default"] = dj_database_url.config(conn_max_age=600)

MEDIA_ROOT = "/data/media/"
STATIC_ROOT = "/data/static/"

# For RabbitMQ
CELERY_BROKER_URL = (
    "amqp://os.environ['DATABASE_USER']:os.environ['DATABASE_PASSWORD']@rabbitmq:5672/"
)
REDIS_HOST = "redis"

# all celery tasks run immediatelly
# from django-celery
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_ALWAYS_EAGER = CELERY_ALWAYS_EAGER  # for celery 4.x
CELERY_TASK_EAGER_PROPAGATES = CELERY_EAGER_PROPAGATES_EXCEPTIONS  # for celery 4.x
CELERY_BROKER_URL = "memory://"
