from rest_framework import status
from rest_framework.exceptions import APIException


class ZenAlreadyExistsError(APIException):
    status_code = 409


class ExecutionEngineException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class MissingParametersException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
