"""
Django settings for djproject project.
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
MANAGE_ROOT = os.path.dirname(PROJECT_ROOT)
REPOSITORY_ROOT = os.path.dirname(MANAGE_ROOT)


def join_to_repo(slug):
    return os.path.join(REPOSITORY_ROOT, slug)


def join_to_project(slug):
    return os.path.join(PROJECT_ROOT, slug)


def join_to_manage(slug):
    return os.path.join(MANAGE_ROOT, slug)


sys.path.insert(0, join_to_manage("djapps"))
sys.path.insert(1, MANAGE_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-@71o$6s6b=j*qabg78#(=*20#isbk5v4)rx&l369vq5(gnt&!*"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "privat24api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "djproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [join_to_project("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "djproject.wsgi.application"

FASTAPI_SETTINGS = {
    "API_V1_PREFIX": "/api",
    "PROJECT_NAME": "BStore",
    "DEBUG": DEBUG,
}

API_BASE_URL = "http://127.0.0.1:8000/api"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASE_OPTIONS = "charset=utf8"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
DEFAULT_CHARSET = "utf-8"
# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
MEDIA_ROOT = join_to_repo("media")
STATIC_ROOT = join_to_repo("allstatic")
STATIC_URL = "static/"
MEDIA_URL = "/media/"
# Additional locations of static files
STATICFILES_DIRS = [join_to_project("static")]
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760 * 10  # 100 MB

try:
    from .base_apps import *
except ImportError:
    sys.stderr.write("Unable to read base_apps.py\n")
    DEBUG = False

try:
    from .base_celery import *
except ImportError:
    sys.stderr.write("Unable to read base_celery.py\n")
    DEBUG = False
