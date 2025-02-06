"""
Celery app and task configuration, all celery related conf should be here.
"""
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queryzen_api.settings')

app = Celery('queryzen_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


def is_execution_engine_working(ping_timeout: int = 1) -> (bool, str):
    """
    Checks whether the execution engine (broker + celery) are up.

    Args:
        ping_timeout: The timeout in seconds for the ping that is sent to the workers.

    Returns:
        A tuple:
            First element: True if both broker and a celery worker can be reached; a query is
            expected to be able to run.
            Second element: An error message, it can pinpoint the offender..
    """
    try:
        result = app.control.inspect(timeout=ping_timeout).ping()
        if not result:
            return False, ('Zen could not be executed, no worker responded to ping.'
                           ' Check that there are there alive workers.')

    except Exception as e: # pylint: disable=W0718 # TODO fix broad exception.
        return False, f'Broker could not be reached be reached: {repr(e)}'

    return True, None
