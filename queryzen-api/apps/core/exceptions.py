from rest_framework.exceptions import APIException


class ZenAlreadyExistsError(APIException):
    status_code = 409
