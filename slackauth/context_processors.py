from django.conf import settings


def login_scope(request):
    return {
        'slack_login_scope': settings.SLACK_LOGIN_SCOPE
    }
