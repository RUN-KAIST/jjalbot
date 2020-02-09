# noinspection PyUnresolvedReferences
import os

from .base import *  # noqa F403,F401

SECRET_KEY = 'adfwjf29fj09fpoad2j^_^2eirn2f2je93r2jf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*'
]

SITE_ID = 4


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
SERVE_MEDIA = True

BIGEMOJI_MAX_ENTRY = 5
