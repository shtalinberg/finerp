import datetime

from django.core import management
from django.utils import timezone

from celery import shared_task
from celery.utils.log import get_task_logger
from privat24api.models import P24ApiSession

from . import settings as pb_conf

logger = get_task_logger(__name__)


@shared_task
def privat24api_get_statements():
    logger.info("run privat24api_get_statements in celery")
    if not pb_conf.PRIVAT24_API_TOKEN:
        logger.info("privat24api_get_statements in celery skiped - Token not Set")
    else:
        try:
            # Sync statement data by using Django management command.
            management.call_command("p24api_get_statements", verbosity=0)
            return "success"
        except Exception as err:
            logger.error(err)
    return None


@shared_task(name="privat24api.tasks.cleanup_p24apisession")
def cleanup_cmdlog(days=60):
    """
    Cleans up the `P24ApiSession` records in the database by deleting the records
    that are older than the specified number of days.
    Parameters:
        days (int, optional): The number of days old a record should be in order to be deleted.
            Defaults to 60.
    """
    deleted = 0
    cutoff_date = timezone.now() - datetime.timedelta(days=days)
    for old_rec in P24ApiSession.objects.filter(created_at__lt=cutoff_date):
        old_rec.delete()
        deleted += 1
    logger.info(f"deleted {deleted} P24ApiSession records")
