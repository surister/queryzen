"""
Django settings for queryzen_api project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

from databases.base import SQLiteDatabase, CrateDatabase

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
test_token = 'django-insecure-fs+y^@*i1o&w1ehn)mhj0gh54@5q0xg_llb7h0@ubof+0pe25e'
SECRET_KEY = os.getenv('DJANGO_KEY',
                       test_token)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('BUILD_ENV', True)
DEBUG = not DEBUG == 'production'

if len(SECRET_KEY) <= 20:
    raise ValueError('DJANGO_KEY has to be bigger than 20 characters')

if not DEBUG and SECRET_KEY == test_token:
    raise ValueError('Configuration error, app is running in production mode and was not provided '
                     'a token, set DJANGO_KEY to a safe 20+ character key.')

###################################################################################
# DEBUG IS ALREADY SET AND VALIDATED AT THIS POINT, IF YOU WANT TO ADD            #
#                                                                                 #
# MORE FEATURES DEPENDING IF WE ARE IN PROD OR NOT, USE DEBUG variable, example:  #
#                                                                                 #
# if not DEBUG:                                                                   #
#     REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (                              #
#             "rest_framework.renderers.JSONRenderer",                            #
#         )                                                                       #
###################################################################################

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'apps.core',

    'rest_framework',
    'django_filters',
    'django_celery_results',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

if DEBUG:
    INSTALLED_APPS.append('apps.testing')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'queryzen_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'queryzen_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )

CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_IMPORTS = ('apps.core.tasks',)

ZEN_DATABASES = {
    'default': SQLiteDatabase('tdd.sqlite'),
    'crate': CrateDatabase()
}

ZEN_TIMEOUT = 2
