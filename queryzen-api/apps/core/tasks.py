import logging

from celery import shared_task
from django.conf import settings

from apps.core.models import QueryZen
from databases.base import Database

logger = logging.getLogger(__name__)


@shared_task
def run_query(target: str, zen_id: str, parameters: dict or None = None):
    zen = QueryZen.objects.get(pk=zen_id)
    db_instance: Database = getattr(settings, 'ZEN_DATABASES').get(target)

    columns, rows = db_instance.execute(zen.query, parameters)

    return {
        'columns': columns,
        'rows': rows,
    }
