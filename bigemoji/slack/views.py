from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import AuthError
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

import hmac
import hashlib
import shlex
import requests

from .tasks import upload_bigemoji
from .provider import SlackProvider


# Create your views here.


def verify_request(request):
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


@csrf_exempt
@require_POST
def index(request):
    if verify_request(request):
        cmd_args = shlex.split(request.POST.get('text'))
        if len(cmd_args) == 1:
            bigemoji_name = cmd_args[0]
            slack_user_id = request.POST.get('user_id')
            team_id = request.POST.get('team_id')
            channel_id = request.POST.get('channel_id')
            response_url = request.POST.get('response_url')

            upload_bigemoji.delay(team_id, channel_id, slack_user_id, bigemoji_name, response_url)
            return HttpResponse()
        else:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': 'The command should contain exactly 1 argument.'
            })
    else:
        return HttpResponseForbidden()


class SlackOAuth2Adapter(OAuth2Adapter):
    provider_id = SlackProvider.id

    access_token_url = 'https://slack.com/api/oauth.access'
    authorize_url = 'https://slack.com/oauth/authorize'
    identity_url = 'https://slack.com/api/users.identity'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token):
        resp = requests.get(
            self.identity_url,
            params={'token': token}
        )

        resp = resp.json()

        if not resp.get('ok'):
            raise OAuth2Error()

        # Fill in their generic info
        info = {
            'name': resp.get('user').get('name'),
            'user': resp.get('user'),
            'team': resp.get('team')
        }

        return info


class SlackLoginView(OAuth2LoginView):
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        if request.GET.get('process', '') in ('login', 'connect'):
            if request.GET.get('scope', '') != settings.SLACK_LOGIN_SCOPE:
                return render_authentication_error(
                    request,
                    provider.id,
                    error=AuthError.DENIED
                )

        return super(SlackLoginView, self).dispatch(request, *args, **kwargs)


oauth2_login = SlackLoginView.adapter_view(SlackOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SlackOAuth2Adapter)
