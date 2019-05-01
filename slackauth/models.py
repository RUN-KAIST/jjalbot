import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.fields import JSONField
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin, SocialToken


class SlackTeam(models.Model):
    id = models.CharField(max_length=settings.SLACK_TEAM_ID_MAX, primary_key=True)
    name = models.CharField(max_length=settings.SLACK_TEAM_NAME_MAX)
    domain = models.CharField(max_length=settings.SLACK_TEAM_DOMAIN_MAX, unique=True)
    verified = models.BooleanField(default=True)
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created', db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated', db_index=True)

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
    name = models.CharField(max_length=settings.SLACK_TEAM_NAME_MAX)
    slack_user_id = models.CharField(max_length=settings.SLACK_USER_ID_MAX)
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated', db_index=True)

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


class SlackTokenBase(models.Model):
    app = models.ForeignKey(SocialApp, on_delete=models.CASCADE)
    token = models.TextField(verbose_name='token')
    extra_data = JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date_created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated', db_index=True)

    class Meta:
        abstract = True


class SlackUserToken(SlackTokenBase):
    slack_account = models.ForeignKey(SlackAccount, on_delete=models.CASCADE)
    scope = models.TextField(blank=True, verbose_name='scope')

    class Meta:
        unique_together = (('app', 'slack_account'),)
        verbose_name = 'slack user token'
        verbose_name_plural = 'slack user tokens'

    def __str__(self):
        return self.token


class SlackBotToken(SlackTokenBase):
    team = models.ForeignKey(SlackTeam, on_delete=models.CASCADE)
    slack_bot_id = models.CharField(max_length=settings.SLACK_BOT_ID_MAX)

    class Meta:
        unique_together = (('app', 'team'),)


class SlackLogin(SocialLogin):
    def __init__(self, access_token=None, *args, **kwargs):
        super(SlackLogin, self).__init__(*args, **kwargs)
        self.access_token = access_token or {}

    def serialize(self):
        ret = super(SlackLogin, self).serialize()
        ret['access_token'] = self.access_token
        return ret

    @classmethod
    def deserialize(cls, data):
        deserialize_instance = get_adapter().deserialize_instance
        account = deserialize_instance(SocialAccount, data['account'])
        user = deserialize_instance(get_user_model(), data['user'])
        if 'token' in data:
            token = deserialize_instance(SocialToken, data['token'])
        else:
            token = None
        email_addresses = []
        for ea in data['email_addresses']:
            email_address = deserialize_instance(EmailAddress, ea)
            email_addresses.append(email_address)
        ret = cls()
        ret.token = token
        ret.account = account
        ret.user = user
        ret.email_addresses = email_addresses
        ret.state = data['state']
        ret.access_token = data['access_token']
        return ret

    def _save_slack_data(self):
        account = self.account
        user_data = account.extra_data.get('user', {})
        team_data = account.extra_data.get('team', {})

        team, _ = SlackTeam.objects.update_or_create(defaults={
            'name': team_data.get('name'),
            'domain': team_data.get('domain'),
            'extra_data': team_data,
        }, pk=team_data.get('id'))

        slack_account, _ = SlackAccount.objects.update_or_create(defaults={
            'slack_user_id': user_data.get('id'),
            'team': team,
            'extra_data': user_data,
        }, account=account)

        app = self.token.app
        scope = self.access_token.get('scope')

        SlackUserToken.objects.update_or_create(defaults={
            'extra_data': self.access_token,
            'token': self.token.token,
            'scope': scope,
        }, app=app, slack_account=slack_account)
        if 'bot' in self.access_token:
            bot_extra_data = self.access_token.get('bot')
            SlackBotToken.objects.update_or_create(defaults={
                'token': bot_extra_data.get('bot_access_token'),
                'slack_bot_id': bot_extra_data.get('bot_user_id'),
                'extra_data': bot_extra_data,
            }, app=app, team=slack_account.team)

    def save(self, request, connect=False):
        super(SlackLogin, self).save(request, connect)
        self._save_slack_data()

    def lookup(self):
        super(SlackLogin, self).lookup()
        if self.is_existing:
            self._save_slack_data()
