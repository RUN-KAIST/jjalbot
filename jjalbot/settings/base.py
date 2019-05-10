"""
Django settings for jjalbot project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
SECRET_KEY = 'adfwjf29fj09fpoad2j^_^2eirn2f2je93r2jf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.slack',

    'bigemoji',
    'bigemoji.slack',
    'bigemoji.slackapp',

    'slackauth',
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

REDIRECT_WEB = None

LOGIN_URL = '/jjalbot/accounts/login'
LOGIN_REDIRECT_URL = '/jjalbot/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/jjalbot/'

BIGEMOJI_APP_ID = 1

BIGEMOJI_MAX_ENTRY = 1000
BIGEMOJI_MAX_SPACE = 10000000
BIGEMOJI_DELETE_ETA = 604800

BIGEMOJI_SLACKAPP_COMMANDS = {
    'bigemoji': [
        '/bigemoji',
        '/jjaltest',
    ],
    'bigemoji_list': [
        '/bigemoji_list',
        '/jjallist',
    ],
}

SITE_ID = 1

SLACK_TEAM_ID_MAX = 10
SLACK_TEAM_NAME_MAX = 255
SLACK_TEAM_DOMAIN_MAX = 21
SLACK_USER_ID_MAX = 10
SLACK_USER_NAME_MAX = 255
SLACK_BOT_ID_MAX = 10

SLACK_LOGIN_SCOPE = 'identity.basic,identity.email,identity.team,identity.avatar'

ACCOUNT_EMAIL_VERIFICATION = 'none'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jjalbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # `allauth` needs this from django
                'django.template.context_processors.request',

                'slackauth.context_processors.login_scope',
            ],
        },
    },
]

WSGI_APPLICATION = 'jjalbot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

SERVE_MEDIA = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/jjalbot/media/"

FILE_UPLOAD_PERMISSIONS = 0o644
