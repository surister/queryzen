from apps.shared.mixins import UUIDMixin

from django.db import models

from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser


class User(AbstractBaseUser, UUIDMixin):
    """
    User override to remove/add more specific columns
    """
    email = models.EmailField(unique=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()
