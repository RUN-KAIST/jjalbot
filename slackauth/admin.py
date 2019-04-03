from django.contrib import admin

from .models import SlackTeam, SlackAccount, SlackUserToken, SlackBotToken


class SlackTeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domain', 'verified', 'was_created_recently',)
    list_filter = ('verified',)


class SlackAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('account',)
    list_display = ('account', 'team', 'slack_user_id', 'was_created_recently')
    list_filter = ('team', 'account__date_joined')


class SlackUserTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'slack_account',)
    list_display = ('app', 'slack_account', 'truncated_scope', 'truncated_token')
    list_filter = ('app', 'slack_account__team')

    def truncated_scope(self, token):
        max_chars = 30
        ret = token.scope
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + '...(truncated)'
        return ret
    truncated_scope.short_description = 'SlackUserToken'

    def truncated_token(self, token):
        max_chars = 30
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + '...(truncated)'
        return ret
    truncated_token.short_description = 'SlackUserToken'


class SlackBotTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'team',)
    list_display = ('app', 'team', 'slack_bot_id', 'truncated_token')
    list_filter = ('app', 'team')

    def truncated_token(self, token):
        max_chars = 40
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + '...(truncated)'
        return ret
    truncated_token.short_description = 'SlackBotToken'


admin.site.register(SlackTeam, SlackTeamAdmin)
admin.site.register(SlackAccount, SlackAccountAdmin)
admin.site.register(SlackUserToken, SlackUserTokenAdmin)
admin.site.register(SlackBotToken, SlackBotTokenAdmin)
