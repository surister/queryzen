# pylint: disable=C0114
from apps.shared.mixins import UUIDMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class QueryzenUserManager(BaseUserManager):
    """Custom manager for QueryzenUser model."""
    def create_user(self, email, password, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class QueryzenUser(AbstractBaseUser, UUIDMixin):
    """Custom user model that uses email as the unique identifier."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)   # Needed for admin access
    is_active = models.BooleanField(default=True)   # Needed for login system

    objects = QueryzenUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)

    def has_perm(self):
        return self.is_superuser

    def has_module_perms(self):
        return self.is_superuser
