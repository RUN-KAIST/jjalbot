from django.conf import settings

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import AuthError
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

import requests

from .provider import SlackProvider


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


class SlackOAuth2LoginView(OAuth2LoginView):
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        if request.GET.get('process', '') in ('login', 'connect'):
            if request.GET.get('scope', '') != settings.SLACK_LOGIN_SCOPE:
                return render_authentication_error(
                    request,
                    provider.id,
                    error=AuthError.DENIED
                )

        return super(SlackOAuth2LoginView, self).dispatch(request, *args, **kwargs)


oauth2_login = SlackOAuth2LoginView.adapter_view(SlackOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SlackOAuth2Adapter)
