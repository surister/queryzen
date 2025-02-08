# pylint: disable=C0114
from rest_framework import status
from rest_framework.exceptions import APIException


class ZenAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT


class ExecutionEngineError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class MissingParametersError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class DatabaseDoesNotExistError(APIException):
    status_code = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
