from functools import wraps

import hashlib
import hmac
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from .models import SlackAccount, SlackTeam


logger = logging.getLogger(__name__)


def slack_login_required(f):
    @wraps(f)
    def wrapper(request, team_id, slack_user_id, *args, **kwargs):
        try:
            team = SlackTeam.objects.get(pk=team_id)
            account_set = SlackAccount.objects.filter(account__user=request.user)
            account = account_set.get(team=team, slack_user_id=slack_user_id)
            return f(request, account, account_set, *args, **kwargs)
        except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist):
            return HttpResponseNotFound()
    return login_required(wrapper)


def _verify_slack_request(request):
    version = 'v0'
    signing_secret = settings.SLACK_APP_SIGNING_SECRET
    x_slack_request_timestamp = request.META.get('HTTP_X_SLACK_REQUEST_TIMESTAMP', '')
    x_slack_signature = request.META.get('HTTP_X_SLACK_SIGNATURE', '')
    request_body = request.body.decode()
    base_string = '{}:{}:{}'.format(version, x_slack_request_timestamp, request_body)
    verifier = '{}={}'.format(version, hmac.new(signing_secret.encode(),
                                                base_string.encode(),
                                                hashlib.sha256).hexdigest())
    return hmac.compare_digest(verifier, x_slack_signature)


def slack_request(f):
    @wraps(f)
    def wrapper(request):
        if _verify_slack_request(request):
            return f(request)
        else:
            logger.info('Slack sent invalid request.')
            return HttpResponseNotFound()
    return csrf_exempt(wrapper)
