from django.db import models
from allauth.socialaccount.models import SocialAccount, SocialApp


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
