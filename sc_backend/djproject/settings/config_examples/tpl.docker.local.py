# Django docker local settings

from djproject.settings.base_localdev import *

DEBUG = True
SSLIFY_DISABLE = True
ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/data/media/"
STATIC_ROOT = "/data/static/"

# For RabbitMQ
CELERY_BROKER_URL = (
    "amqp://os.environ['DATABASE_USER']:os.environ['DATABASE_PASSWORD']@rabbitmq:5672/"
)
REDIS_URL = f"redis://redis:6377"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'] or '',
    }
}
