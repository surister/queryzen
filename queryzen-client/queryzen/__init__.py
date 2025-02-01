# pylint: disable=C0114

from os import getenv
import logging

from .exceptions import IncompatibleAPI
from .queryzen import QueryZen, Zen, AUTO
from .constants import DEFAULT_COLLECTION



def strtobool(val) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if isinstance(val, bool):
        return val

    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f'invalid truth value {val}')


__version__ = 1.22

# We test the unit tests against the backend itself to ensure 100% client/backend compatability.
# The version of the API that we tested against.
# Do not modify, it is automatically updated at publish time.
API_VERSION_COMPATIBLE = 1.23

# Set this to True in publish time.
# For extra security this can be enabled at run time, it can either debug.warn or raise an exception
# if we are not 100% sure that the client is compatible with the backend, a situation where this can
# happen is if the version of the backend gets updated but the user does not update the client,
# the default 'sane' option is to just warn the user, as a 'friendly' reminder that he should
# update the QueryZen client.
# Fixme make this getenv result be interpreted as Python 'True/False'.
# Fixme make a step in the CI that checks that this is True in publish time.
#

ENFORCE_COMPATABILITY = strtobool(getenv('QUERYZEN_ENFORCE_COMPATABILITY_RUNTIME', 'false'))

# What to do if we find an incompatibility, set to raise in publish.
ENFORCE_COMPATABILITY_ACTION = getenv('QUERYZEN_ENFORCE_COMPATABILITY_RUNTIME_ACTION', 'warn')


def get_api_version():
    # Get api version and compare it to API_VERSION_COMPATIBLE.
    return 0


def is_api_compatible(version):
    return API_VERSION_COMPATIBLE == version


# Question, do we check only this at publish time or runtime?
if ENFORCE_COMPATABILITY:
    backend_version = get_api_version()
    if not is_api_compatible(backend_version):
        message = f"""
        Package version {__version__!r} compatibility is untested for backend version
        {backend_version!r}, compatibility is only tested for {API_VERSION_COMPATIBLE!r},
        please update the package to the latest version.
        
        You can turn this off by setting the env variable 'ENFORCE_COMPATABILITY' to 'false'.
        
        If the package is in the latest version and this still triggers, there is a bug, please
        report this message in a github issue at:
        https://github.com/surister/queryzen/issues/new/choose
                """
        if ENFORCE_COMPATABILITY_ACTION == 'raise_exception':
            raise IncompatibleAPI(message)
        else:
            logging.warning(message)

__all__ = [
    'QueryZen',
    'Zen',
    'DEFAULT_COLLECTION',
    'AUTO'
]
