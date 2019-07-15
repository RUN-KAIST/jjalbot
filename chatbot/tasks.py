from celery import shared_task

from django.core.cache import cache

import re

from slackauth.models import SlackBotToken, SlackTeam
from slackauth.utils import slack_api_call


def _is_bot(team_id, user_id, token):
    uid = '{}_{}'.format(team_id, user_id)
    is_bot = cache.get(uid)
    if is_bot is None:
        user_info = slack_api_call(
            'users.info', token,
            user=user_id
        )

        # If user information cannot be fetched, don't respond
        # and don't save to cache; just take a rain check.
        if not user_info.get('ok'):
            return True

        is_bot = user_info.get('user').get('is_bot')
        cache.set(uid, is_bot)
    return is_bot


@shared_task
def handle_message(req):
    team_id = req.get('team_id')
    event = req.get('event')
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    try:
        team = SlackTeam.objects.get(pk=team_id)
        bot_token = SlackBotToken.objects.get(team=team)
        if not _is_bot(team_id, user_id, bot_token.token):
            format_dict = {
                'user_id': user_id,
            }
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
    except (SlackTeam.DoesNotExist, SlackBotToken.DoesNotExist):
        pass
