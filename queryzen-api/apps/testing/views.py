# pylint: skip-file
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

User = get_user_model()


@api_view(('GET',))
def clean_up_db(request):
    """Cleans up all objects in database, only used in CI - testing."""
    from django.apps import apps
    from django.conf import settings

    # Only allows this if DEBUG is True.
    if settings.DEBUG:
        for model in apps.get_models():
            model.objects.all().delete()
    else:
        assert False

    # Create a new testing user for auth
    User.objects.get_or_create(email="test@test.com", password=make_password('test'))

    return Response(status=status.HTTP_200_OK)
