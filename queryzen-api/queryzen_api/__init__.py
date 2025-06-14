# pylint: skip-file
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
import os

from .celery import app as celery_app

__all__ = ('celery_app',)


# Deprecated distutils.utils.strtobool
def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if isinstance(val, bool):
        return val

    if not isinstance(val, (bool, str)):
        raise TypeError(f'type should be bool or str, not {type(val)!r}')

    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f'invalid truth value {val}')


def get_split_env(env_name, default):
    """Get a comma-separated list of values from an environment variable
    Returns:
        List of strings
    """
    env = os.getenv(env_name)
    return env.split(',') if env else default
