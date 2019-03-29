from django.contrib.auth import get_user_model


def save_slack_token(sender, **kwargs):
    from allauth.socialaccount.models import SocialLogin
    from .models import SlackToken

    # Various checks for our use
    if 'request' in kwargs and 'sociallogin' in kwargs and sender in (
        get_user_model(),
        SocialLogin
    ):
        sociallogin = kwargs['sociallogin']

        assert isinstance(sociallogin, SocialLogin)

        if sociallogin.is_existing:

            app = sociallogin.token.app

            if app.provider == 'slack':
                account = sociallogin.account
                scopes = sociallogin.state.get('scope', '')

                # TODO: Handle race conditions...
                try:
                    slack_token = SlackToken.objects.get(app=app, account=account, scopes=scopes)
                except SlackToken.DoesNotExist:
                    slack_token = SlackToken()

                slack_token.app = app
                slack_token.account = account
                slack_token.token = sociallogin.token.token
                slack_token.token_secret = sociallogin.token.token_secret
                slack_token.expires_at = sociallogin.token.expires_at
                slack_token.scopes = scopes
                slack_token.save()


def save_slack_data(sender, **kwargs):
    from allauth.socialaccount.models import SocialLogin
    from .models import SlackTeam, SlackAccount

    # Various checks for our use
    if 'request' in kwargs and 'sociallogin' in kwargs and sender in (
            get_user_model(),
            SocialLogin
    ):
        sociallogin = kwargs['sociallogin']

        assert isinstance(sociallogin, SocialLogin)

        if sociallogin.is_existing:
            app = sociallogin.token.app

            if app.provider == 'slack':
                account = sociallogin.account
                user_data = account.extra_data.get('user', {})
                team_data = account.extra_data.get('team', {})

                # TODO: Handle race conditions...
                try:
                    team = SlackTeam.objects.get(pk=team_data.get('id', ''))
                except SlackTeam.DoesNotExist:
                    team = SlackTeam()

                team.id = team_data.get('id')
                team.name = team_data.get('name', '')
                team.domain = team_data.get('domain', '')
                team.extra_data = team_data
                team.save()

                # TODO: Handle race conditions...
                try:
                    slack_account = SlackAccount.objects.get(account=account)
                except SlackAccount.DoesNotExist:
                    slack_account = SlackAccount()

                slack_account.account = account
                slack_account.slack_user_id = user_data.get('id', '')
                slack_account.team = team
                slack_account.extra_data = user_data
                slack_account.save()
