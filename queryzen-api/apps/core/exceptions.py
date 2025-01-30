from rest_framework import status
from rest_framework.exceptions import APIException


class ZenAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
