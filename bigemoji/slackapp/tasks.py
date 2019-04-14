from django.conf import settings
from django.db.models import Q

from celery import shared_task
import re
import os
import datetime

from .utils import slack_delayed_response, slack_api_call


@shared_task
def upload_bigemoji(team_id, channel_id, slack_user_id, bigemoji_name, response_url):
    from ..models import BigEmoji, BigEmojiStorage
    from slackauth.models import SlackTeam, SlackAccount, SlackUserToken

    try:
        team = SlackTeam.objects.get(pk=team_id)
        storage = team.bigemojistorage
        bigemoji = BigEmoji.objects.get(storage=storage, emoji_name=bigemoji_name)
        account = SlackAccount.objects.get(team=team, slack_user_id=slack_user_id)
        token = SlackUserToken.objects.get(
            Q(scope__contains='files:write:user') & Q(scope__contains='chat:write:user'),
            app_id=settings.BIGEMOJI_APP_ID,
            slack_account=account
        )
        delete_eta = team.bigemojistorage.delete_eta

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
                                            team_id,
                                            channel_id,
                                            slack_user_id,
                                            bigemoji_name,
                                            timestamp,
                                            file_id,
                                            token.token,
                                        ])
        else:
            slack_delayed_response(response_url, 'Something went wrong. Please try again!')

    except BigEmoji.DoesNotExist:
        slack_delayed_response(response_url, 'That emoji does not exist!')
    except (
        BigEmojiStorage.DoesNotExist,
        SlackTeam.DoesNotExist,
        SlackAccount.DoesNotExist,
        SlackUserToken.DoesNotExist
    ) as e:
        slack_delayed_response(response_url, 'You should grant us some permissions. '
                                             'Please visit `https://run.kaist.ac.kr/jjalbot/`.')
    except ValueError:
        slack_delayed_response(response_url, 'Something went wrong. Please try again!')


@shared_task
def delete_bigemoji(team_id, channel_id, slack_user_id, bigemoji_name, timestamp, file_id, token):
    def try_delete(trying_token):
        success = False
        resp_json = slack_api_call(
            'chat.update',
            trying_token,
            channel=channel_id,
            text='[BigEmoji:{}]'.format(bigemoji_name),
            ts=timestamp,
            as_user=True
        )
        if resp_json.get('ok'):
            success = slack_api_call(
                'files.delete',
                trying_token,
                file=file_id
            ).get('ok')
        return success

    # Try with passed token, or fetch from DB if fails.
    if not try_delete(token):
        from slackauth.models import SlackAccount, SlackUserToken

        try:
            account = SlackAccount.objects.get(team_id=team_id, slack_user_id=slack_user_id)
            new_token = SlackUserToken.objects.get(
                Q(scope__contains='files:write:user') & Q(scope__contains='chat:write:user'),
                app_id=settings.BIGEMOJI_APP_ID,
                slack_account=account,
            )
            try_delete(new_token)
        except (SlackAccount.DoesNotExist, SlackUserToken.DoesNotExist, ValueError):
            pass


@shared_task
def bigemoji_list(team_id, response_url):
    from ..models import BigEmojiStorage
    from slackauth.models import SlackTeam

    try:
        team = SlackTeam.objects.get(pk=team_id)
        storage = team.bigemojistorage
        bigemoji_name_list = []
        for bigemoji in storage.bigemoji_set.all():
            bigemoji_name_list.append(bigemoji.emoji_name)
        if bigemoji_name_list:
            slack_delayed_response(response_url, ', '.join(bigemoji_name_list))
        else:
            slack_delayed_response(response_url, 'No BigEmoji exists!')
    except (SlackTeam.DoesNotExist, BigEmojiStorage.DoesNotExist):
        slack_delayed_response(response_url, 'Your workspace is not yet allowed to add BigEmojis. '
                                             'Please contact the administrators.')
