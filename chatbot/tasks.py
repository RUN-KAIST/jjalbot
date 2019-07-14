from celery import shared_task

import re

from slackauth.models import SlackBotToken, SlackTeam
from slackauth.utils import slack_api_call


@shared_task
def handle_message(req):
    team_id = req.get('team_id')
    event = req.get('event')
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    team = SlackTeam.objects.get(pk=team_id)
    bot_token = SlackBotToken.objects.get(team=team)

    format_dict = {
        'user_id': user_id,
    }
    if user_id != bot_token.slack_bot_id:
        chat_manuals = team.chatmanualstorage.chatmanual_set.all()
        for chat_manual in chat_manuals:
            m = re.match(chat_manual.trigger_re, text)
            if m:
                format_dict.update(m.groupdict())
                response = chat_manual.response.format(**format_dict)
                slack_api_call(
                    'chat.postMessage', bot_token.token,
                    channel=channel_id,
                    as_user=True,
                    text=response
                )
                break
