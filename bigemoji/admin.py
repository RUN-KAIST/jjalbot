from django.contrib import admin

from .models import BigEmoji, BigEmojiStorage

# Register your models here.


class BigEmojiInlineAdmin(admin.TabularInline):
    model = BigEmoji
    extra = 0


class BigEmojiStorageAdmin(admin.ModelAdmin):
    list_display = ('team', 'max_entry', 'max_size', 'occupied')
    readonly_fields = ('occupied',)
    inlines = (BigEmojiInlineAdmin,)


class BigEmojiAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['storage', 'owner', 'emoji_name', 'image_file', 'alias']}),
    ]
    list_display = ('storage', 'owner', 'emoji_name', 'image_file', 'date_created', 'alias')
    list_filter = ['date_created', 'storage', 'owner']


admin.site.register(BigEmoji, BigEmojiAdmin)
admin.site.register(BigEmojiStorage, BigEmojiStorageAdmin)
