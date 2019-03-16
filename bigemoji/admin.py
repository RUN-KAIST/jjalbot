from django.contrib import admin

from .models import BigEmoji

# Register your models here.


class BigEmojiAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['author', 'image']}),
    ]
    list_display = ('author', 'image', 'date_created', 'was_created_recently')
    list_filter = ['date_created']


admin.site.register(BigEmoji, BigEmojiAdmin)
