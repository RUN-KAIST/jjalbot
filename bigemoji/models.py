import datetime

from django.db import models
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount

# Create your models here.


def team_directory(instance, filename):
    return '{}/{}_{}'.format(instance.team_id,
                             instance.emoji_name,
                             filename)


class BigEmoji(models.Model):
    author = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    team_id = models.CharField(max_length=10)
    emoji_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=team_directory)
    date_created = models.DateTimeField(auto_now=True, verbose_name='date created')

    class Meta:
        unique_together = (('team_id', 'emoji_name'),)

    def __str__(self):
        return self.emoji_name

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_created <= now
    was_created_recently.admin_order_field = 'date_created'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Created recently?'


class BigEmojiAlias(models.Model):
    author = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    bigemoji = models.ForeignKey(BigEmoji, on_delete=models.CASCADE)
    alias_name = models.CharField(max_length=100)

    def __str__(self):
        return self.alias_name
