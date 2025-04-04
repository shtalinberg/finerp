import os
import sys

from celery import Celery

ENV_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(ENV_ROOT, 'djapps'))
sys.path.insert(2, os.path.join(ENV_ROOT))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djproject.settings')

app = Celery('djproject')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()  # lambda: settings.INSTALLED_APPS)
