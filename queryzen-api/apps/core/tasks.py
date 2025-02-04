import datetime
import logging
import sqlite3

from celery import shared_task
from django.conf import settings
from django.shortcuts import get_object_or_404

from apps.core.models import QueryZen, Execution
from apps.core.serializers import ZenExecutionResponseSerializer
from databases.base import Database

logger = logging.getLogger(__name__)


@shared_task
def run_query(database: str, pk: str, parameters: dict | None = None):
    executed_at = datetime.datetime.now(datetime.UTC)
    zen = get_object_or_404(QueryZen, pk=pk)
    execution = Execution(zen=zen)
    db_instance: Database = getattr(settings, 'ZEN_DATABASES').get(database)

    error: str | None = None
    columns = rows = []
    try:
        columns, rows, query = db_instance.execute(zen.query, parameters)
        execution.state = Execution.State.VALID
        execution.query = query
        zen.state = QueryZen.State.VALID
    except Exception as e:
        error = str(e)
        execution.state = Execution.State.INVALID
        zen.state = QueryZen.State.INVALID

    zen.save()
    execution.save()

    finished_at = datetime.datetime.now(datetime.UTC)
    execution_time = (finished_at - executed_at).total_seconds() * 1000 # milliseconds

    response = ZenExecutionResponseSerializer(
        {
            'id': execution.pk,
            'columns': columns,
            'rows': rows,
            'execution_time_ms': execution_time,
            'error': error if error else None,
            'executed_at': executed_at,
            'finished_at': finished_at,
            'query': query
        }
    )
    return response.data
