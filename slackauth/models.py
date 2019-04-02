import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from allauth.socialaccount.fields import JSONField
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin


class SlackTeam(models.Model):
    id = models.CharField(max_length=settings.SLACK_TEAM_ID_MAX, primary_key=True)
    name = models.CharField(max_length=settings.SLACK_TEAM_NAME_MAX)
    domain = models.CharField(max_length=settings.SLACK_TEAM_DOMAIN_MAX, unique=True)
    verified = models.BooleanField(default=False)
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now=True, verbose_name='date created')

    def __str__(self):
        return '{}.slack.com'.format(self.domain)

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_created <= now
    was_created_recently.admin_order_field = 'date_created'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Created recently?'


class SlackAccount(models.Model):
    account = models.OneToOneField(SocialAccount,
                                   on_delete=models.CASCADE,
                                   primary_key=True)
    team = models.ForeignKey(SlackTeam, on_delete=models.CASCADE)
    slack_user_id = models.CharField(max_length=settings.SLACK_USER_ID_MAX)
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now=True, verbose_name='date created')

    class Meta:
        unique_together = (('team', 'slack_user_id'),)

    def __str__(self):
        return self.account.__str__()

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_created <= now
    was_created_recently.admin_order_field = 'date_created'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Created recently?'


class SlackToken(models.Model):
    USER = 0
    BOT = 1
    WORKSPACE = 2
    LEGACY = 3
    VERIFICATION = 4
    TOKEN_TYPE_CHOICES = (
        (USER, 'User token'),
        (BOT, 'Bot token'),
        (WORKSPACE, 'Workspace token'),
        (LEGACY, 'Legacy token'),
        (VERIFICATION, 'Verification token'),
    )
    token_type = models.IntegerField(choices=TOKEN_TYPE_CHOICES)
    app = models.ForeignKey(SocialApp, on_delete=models.CASCADE)
    # TODO: Connect SlackToken to SlackAccount
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    token = models.TextField(verbose_name='token')
    token_secret = models.TextField(blank=True, verbose_name='token secret')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='expires at')
    scopes = models.TextField(blank=True, verbose_name='scopes')
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now=True, verbose_name='date created')

    class Meta:
        unique_together = (('app', 'account', 'token_type', 'scopes'),)
        verbose_name = 'slack application token'
        verbose_name_plural = 'slack application tokens'

    def __str__(self):
        return self.token


class SlackLogin(SocialLogin):
    def __init__(self, access_token, *args, **kwargs):
        super(SlackLogin, self).__init__(*args, **kwargs)
        self.access_token = access_token

    def _save_slack_token(self):
        app = self.token.app
        account = self.account
        scopes = self.access_token['scope']
        SlackToken.objects.update_or_create(defaults={
            'token': self.token.token,
            'token_secret': self.token.token_secret,
            'expires_at': self.token.expires_at,
            'extra_data': self.access_token,
        }, app=app, account=account, token_type=SlackToken.USER, scopes=scopes)
        if 'bot' in self.access_token:
            SlackToken.objects.update_or_create(defaults={
                'token': self.access_token.get('bot').get('bot_access_token'),
                'token_secret': '',
                'expires_at': None,
                'extra_data': self.access_token.get('bot'),
            }, app=app, account=account, token_type=SlackToken.BOT, scopes='')

    def _save_slack_data(self):
        account = self.account
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

    def save(self, request, connect=False):
        super(SlackLogin, self).save(request, connect)
        self._save_slack_token()
        self._save_slack_data()

    def lookup(self):
        super(SlackLogin, self).lookup()
        self._save_slack_token()
        self._save_slack_data()
