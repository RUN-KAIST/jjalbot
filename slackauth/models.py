import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from allauth.socialaccount.fields import JSONField
from allauth.socialaccount.models import SocialAccount, SocialApp


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
    app = models.ForeignKey(SocialApp, on_delete=models.CASCADE)
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    token = models.TextField(verbose_name='token')
    token_secret = models.TextField(blank=True, verbose_name='token secret')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='expires at')
    scopes = models.TextField(verbose_name='scopes')
    date_created = models.DateTimeField(auto_now=True, verbose_name='date created')

    class Meta:
        unique_together = (('app', 'account', 'scopes'),)
        verbose_name = 'slack application token'
        verbose_name_plural = 'slack application tokens'

    def __str__(self):
        return self.token
