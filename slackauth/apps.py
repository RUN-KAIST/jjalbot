from django.apps import AppConfig

from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import pre_social_login, social_account_added

from .signals import save_slack_token, save_slack_data


class SlackAuthConfig(AppConfig):
    name = 'slackauth'

    def ready(self):
        pre_social_login.connect(save_slack_token)

        # The account is not saved if the user is logging
        # in for the first time.
        user_signed_up.connect(save_slack_token)

        social_account_added.connect(save_slack_data)
        user_signed_up.connect(save_slack_data)
