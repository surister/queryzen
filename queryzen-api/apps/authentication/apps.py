import logging

from django.apps import AppConfig
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        """Generate a user"""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if User.objects.count() == 0:
            email = "admin@admin.com"
            password = get_random_string(32)
            User.objects.create(
                email=email,
                password=make_password(password),
                is_superuser=True
            )

            msg = f'DEFAULT ADMIN USER:\n - EMAIL: {email}\n - PASSWORD: {password}'
            print(msg)
            logger.log(logging.INFO, msg)
