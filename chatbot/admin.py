from django.contrib import admin

from .models import ChatManual, ChatManualStorage


class ChatManualInlineAdmin(admin.TabularInline):
    model = ChatManual
    extra = 0


class ChatManualStorageAdmin(admin.ModelAdmin):
    list_display = ('team', 'max_entry', 'entries')
    readonly_fields = ('entries',)
    inlines = (ChatManualInlineAdmin,)


class ChatManualAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['storage', 'owner', 'trigger_re', 'response']}),
    ]
    list_display = ('storage', 'owner', 'trigger_re', 'response', 'date_created')
    list_filter = ['date_created', 'storage', 'owner']


admin.site.register(ChatManual, ChatManualAdmin)
admin.site.register(ChatManualStorage, ChatManualStorageAdmin)
