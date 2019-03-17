from django.contrib import admin

from .models import BigEmoji

# Register your models here.


class BigEmojiAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['author', 'emoji_name', 'image']}),
    ]
    list_display = ('author', 'emoji_name', 'image', 'date_created', 'was_created_recently')
    list_filter = ['date_created', 'author']


admin.site.register(BigEmoji, BigEmojiAdmin)
