from django import forms
from .models import BigEmoji


class BigEmojiForm(forms.ModelForm):

    class Meta:
        model = BigEmoji
        fields = ['emoji_name', 'image_file']


class BigEmojiAliasForm(forms.ModelForm):
    class Meta:
        model = BigEmoji
        fields = ['emoji_name', 'alias']

    def __init__(self, storage, *args, **kwargs):
        super(BigEmojiAliasForm, self).__init__(*args, **kwargs)
        if storage is None:
            self.fields['alias'].queryset = BigEmoji.objects.none()
        else:
            self.fields['alias'].queryset = BigEmoji.objects.filter(storage=storage, alias__isnull=True)
