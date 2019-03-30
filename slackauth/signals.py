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

                SlackToken.objects.update_or_create(defaults={
                    'token': sociallogin.token.token,
                    'token_secret': sociallogin.token.token_secret,
                    'expires_at': sociallogin.token.expires_at,
                }, app=app, account=account, scopes=scopes)


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

                team, _ = SlackTeam.objects.update_or_create(defaults={
                    'name': team_data.get('name'),
                    'domain': team_data.get('domain'),
                    'extra_data': team_data,
                }, pk=team_data.get('id'))

                SlackAccount.objects.update_or_create(defaults={
                    'slack_user_id': user_data.get('id'),
                    'team': team,
                    'extra_data': user_data,
                }, account=account)
