from django import forms
from .models import BigEmoji, BigEmojiAlias


class BigEmojiForm(forms.ModelForm):
    class Meta:
        model = BigEmoji
        fields = ['emoji_name', 'image']


class BigEmojiAliasForm(forms.ModelForm):
    class Meta:
        model = BigEmojiAlias
        fields = ['alias_name', 'bigemoji']
