import datetime

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from slackauth.models import SlackTeam, SlackAccount


def team_directory(instance, filename):
    return '{}/{}_{}'.format(instance.team.id,
                             instance.emoji_name,
                             filename)


class BigEmojiFullException(Exception):
    pass


class BigEmojiStorage(models.Model):
    team = models.OneToOneField(SlackTeam, on_delete=models.CASCADE)
    occupied = models.IntegerField()
    max_size = models.IntegerField(default=10000000)
    entries = models.IntegerField()
    max_entry = models.IntegerField(default=1000)
    delete_eta = models.IntegerField(default=3600)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated')

    def __str__(self):
        return self.team.__str__()


class BigEmoji(models.Model):
    owner = models.ForeignKey(SlackAccount, on_delete=models.CASCADE)
    storage = models.ForeignKey(BigEmojiStorage, on_delete=models.CASCADE)
    emoji_name = models.CharField(max_length=100)
    image_file = models.ImageField(upload_to=team_directory, null=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    alias = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('storage', 'emoji_name'),)

    def __str__(self):
        return self.emoji_name

    @property
    def team(self):
        return self.storage.team

    @property
    def is_alias(self):
        return self.alias is not None

    def clean(self):
        if self.image_file is None and self.alias is None:
            raise ValidationError('The BigEmoji should contain an image or should be an alias.')

        if self.alias is not None and self.alias.alias is not None:
            raise ValidationError('Cannot alias an alias.')

    @property
    def image(self):
        if self.alias is not None:
            return self.alias.image_file
        else:
            return self.image_file

    @property
    def size(self):
        if self.alias is not None:
            return 0
        else:
            return self.image_file.size

    @transaction.atomic
    def save_emoji(self):
        storage = BigEmojiStorage.objects.select_for_update().get(pk=self.storage_id)
        if storage.entries < storage.max_entry:
            if self.alias is not None or storage.occupied + self.image_file.size < storage.max_size:
                self.save()
                if not self.is_alias:
                    storage.occupied += self.image_file.size
                storage.entries += 1
                storage.save()
            else:
                raise BigEmojiFullException()
        else:
            raise BigEmojiFullException()

    @transaction.atomic
    def delete_emoji(self):
        storage = BigEmojiStorage.objects.select_for_update().get(pk=self.storage_id)
        if not self.is_alias:
            storage.occupied -= self.image_file.size
        storage.entries -= 1
        storage.save()
        self.delete()

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_created <= now
    was_created_recently.admin_order_field = 'date_created'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Created recently?'


@receiver(post_delete, sender=BigEmoji)
def remove_file_on_delete(sender, instance, **kwargs):
    if not instance.is_alias:
        instance.image_file.delete(save=False)
