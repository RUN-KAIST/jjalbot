from django.db import models

from slackauth.models import SlackTeam, SlackAccount


class ChatManualStorage(models.Model):
    team = models.OneToOneField(SlackTeam, on_delete=models.CASCADE)
    entries = models.IntegerField(default=0)
    max_entry = models.IntegerField(default=1000)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated')

    def __str__(self):
        return self.team.__str__()


class ChatManual(models.Model):
    owner = models.ForeignKey(SlackAccount, on_delete=models.CASCADE)
    storage = models.ForeignKey(ChatManualStorage, on_delete=models.CASCADE)
    trigger_re = models.CharField(max_length=255, blank=False, null=False)
    response = models.CharField(max_length=255, blank=False, null=False)
    eval_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated')

    class Meta:
        ordering = ('eval_order',)

    def __str__(self):
        return self.trigger_re
