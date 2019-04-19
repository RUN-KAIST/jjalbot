from django.conf import settings
from django.contrib import messages
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

from .models import SlackLogin
from .provider import SlackProvider


class SlackSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        # Entering this function means that there is a duplicate email.
        messages.add_message(
            request,
            messages.WARNING,
            'It looks like there is already an account with that email. '
            'Login with that account and connect to this if possible.'
        )

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
