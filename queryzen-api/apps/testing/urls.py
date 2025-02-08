# pylint: skip-file
from django.conf import settings
from django.urls import path
from .views import clean_up_db

urlpatterns = [
    path('clean_db', clean_up_db)
] if settings.DEBUG else []  # Only load path if settings.DEBUG is True.
