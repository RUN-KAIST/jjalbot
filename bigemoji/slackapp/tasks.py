from django.db.models import Q
from django.utils import timezone

from celery import shared_task
import re
import os
import datetime

from .utils import slack_delayed_response, slack_api_call


@shared_task
def upload_bigemoji(team_id, channel_id, slack_user_id, bigemoji_name, response_url):
    from ..models import BigEmoji
    from slackauth.models import SlackTeam, SlackAccount, SlackToken

    try:
        team = SlackTeam.objects.get(pk=team_id)
        bigemoji = BigEmoji.objects.get(team=team, emoji_name=bigemoji_name)
        account = SlackAccount.objects.get(team=team, slack_user_id=slack_user_id)
        token = SlackToken.objects.filter(Q(account=account.account),
                                          Q(scopes__contains='files:write:user'),
                                          Q(scopes__contains='chat:write:user'),
                                          Q(expires_at__lte=timezone.now())
                                          | Q(expires_at=None))[0:1].get()
        delete_eta = team.delete_eta

        resp_json = slack_api_call(
            'files.upload',
            token.token,
            channels=channel_id,
            file=(
                # Remove non-asciis from filename
                re.sub(r'[^\x00-\x7f]', r'_', os.path.basename(bigemoji.image.name)),
                bigemoji.image
            ),
            title=bigemoji.emoji_name
        )

        if resp_json.get('ok'):
            file_info = resp_json.get('file')
            file_id = file_info.get('id')
            shared_info = file_info.get('shares', {})
            timestamp = ''
            for channel_info in shared_info.values():
                if channel_id in channel_info:
                    timestamp = min(map(lambda info: info.get('ts', ''), channel_info[channel_id]))
                    break
            delete_bigemoji.apply_async(eta=datetime.datetime.now() + datetime.timedelta(seconds=delete_eta),
                                        args=[
                                            channel_id,
                                            timestamp,
                                            file_id,
                                            bigemoji.pk,
                                            token.pk
                                        ])
        else:
            slack_delayed_response(response_url, 'Something went wrong. Please try again!')

    except BigEmoji.DoesNotExist:
        slack_delayed_response(response_url, 'That emoji does not exist!')
    except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist, SlackToken.DoesNotExist) as e:
        print(e)
        slack_delayed_response(response_url, 'You should grant us some permissions. '
                                             'Please visit `https://run.kaist.ac.kr/jjalbot/`.')
    except ValueError:
        slack_delayed_response(response_url, 'Something went wrong. Please try again!')


@shared_task
def delete_bigemoji(channel_id, timestamp, file_id, bigemoji_pk, token_pk):
    from ..models import BigEmoji
    from slackauth.models import SlackToken

    try:
        bigemoji = BigEmoji.objects.get(pk=bigemoji_pk)
        token = SlackToken.objects.get(pk=token_pk)

        slack_api_call(
            'chat.update',
            token.token,
            channel=channel_id,
            text='[BigEmoji:{}]'.format(bigemoji.emoji_name),
            ts=timestamp,
            as_user=True
        )

        slack_api_call(
            'files.delete',
            token.token,
            file=file_id
        )
    except (BigEmoji.DoesNotExist, SlackToken.DoesNotExist, ValueError):
        pass
