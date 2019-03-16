from django.forms import ModelForm
from .models import BigEmoji, BigEmojiAlias


class BigEmojiForm(ModelForm):
    class Meta:
        model = BigEmoji
        fields = ['emoji_name', 'image']


class BigEmojiAliasForm(ModelForm):
    class Meta:
        model = BigEmojiAlias
        fields = ['alias_name', 'bigemoji']
