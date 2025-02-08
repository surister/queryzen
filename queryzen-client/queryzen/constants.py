"""Constants for QueryZen"""
import os

# The default collection of queryzen is 'main', if not specified
# we will always query this.
DEFAULT_COLLECTION = os.getenv('QUERYZEN_DEFAULT_COLLECTION', 'main')
LOCAL_URL = 'http://localhost:8000'
BACKEND_URL = os.getenv('QUERYZEN_API_URL', LOCAL_URL)

# The default database what will be used to EXECUTE zens. Zens are saved and deleted
# from the backend database, which is different.
DEFAULT_DATABASE = os.getenv('QUERYZEN_DEFAULT_DATABASE', 'default')

# Timeout for HTTP petitions to the backend, not to be confused to the timeout we set when
# running a zen which timeouts the execution of the zen.
DEFAULT_HTTP_TIMEOUT = os.getenv('QUERYZEN_HTTP_TIMEOUT', 60)

# Set lower when developing for faster errors.
DEFAULT_ZEN_EXECUTION_TIMEOUT = os.getenv('QUERYZEN_EXECUTION_TIMEOUT', 60)
