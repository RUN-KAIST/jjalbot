from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import AuthError
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.views import SignupView

import requests
import logging

from .models import SlackLogin
from .provider import SlackProvider


logger = logging.getLogger(__name__)


class SlackSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        self.sociallogin = None
        data = request.session.get('socialaccount_sociallogin')
        if data:
            self.sociallogin = SlackLogin.deserialize(data)
        if not self.sociallogin:
            return HttpResponseRedirect(reverse('account_login'))
        return super(SignupView, self).dispatch(request, *args, **kwargs)


slack_signup = SlackSignupView.as_view()


class SlackOAuth2Adapter(OAuth2Adapter):
    provider_id = SlackProvider.id

    access_token_url = 'https://slack.com/api/oauth.access'
    authorize_url = 'https://slack.com/oauth/authorize'
    identity_url = 'https://slack.com/api/users.identity'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        response = {
            'access_token': kwargs.get('response'),
            'slack_data': extra_data
        }
        return self.get_provider().sociallogin_from_response(request,
                                                             response)

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

        process = request.GET.get('process')
        scope = request.GET.get('scope')

        if process in ('login', 'connect') and scope != settings.SLACK_LOGIN_SCOPE:
            logger.info('User {} with wrong scope: {}'.format(process, scope))

            return render_authentication_error(
                request,
                provider.id,
                error=AuthError.DENIED
            )

        logger.debug('User {} with scope {}'.format(process, scope))

        return super(SlackOAuth2LoginView, self).dispatch(request, *args, **kwargs)


oauth2_login = SlackOAuth2LoginView.adapter_view(SlackOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SlackOAuth2Adapter)
