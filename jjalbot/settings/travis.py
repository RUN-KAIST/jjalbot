from .base import *   # noqa F403,F401


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
