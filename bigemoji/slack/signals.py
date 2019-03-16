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
