from .base import *


SECRET_KEY = "abcdefghijklmnopqrstuvwxyz1234567890"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jjalbot',
        'USER': 'jjalbot',
        'PASSWORD': 'travis',
        'HOST': 'localhost',
        'PORT': '',
    }
}
