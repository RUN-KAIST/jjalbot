from django.contrib import admin

from .models import BigEmoji

# Register your models here.


class BigEmojiAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['team', 'owner', 'emoji_name', 'image']}),
    ]
    list_display = ('team', 'owner', 'emoji_name', 'image', 'date_created', 'was_created_recently')
    list_filter = ['date_created', 'team', 'owner']


admin.site.register(BigEmoji, BigEmojiAdmin)
