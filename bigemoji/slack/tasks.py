from celery import shared_task
import requests
import re
import os
import datetime


@shared_task
def upload_bigemoji(channel_id, bigemoji_pk, token_pk, response_url, delete_eta):
    from ..models import BigEmoji
    from .models import SlackToken

    try:
        bigemoji = BigEmoji.objects.get(pk=bigemoji_pk)
        token = SlackToken.objects.get(pk=token_pk)

        headers = {
            'Authorization': 'Bearer {}'.format(token.token)
        }
        body = {
            'channels': channel_id,
            'title': bigemoji.emoji_name
        }

        # Remove non-asciis from filename
        files = {
            'file': (
                re.sub(r'[^\x00-\x7f]', r'', os.path.basename(bigemoji.image.name)),
                bigemoji.image
            )
        }

        resp_json = requests.post(
            'https://slack.com/api/files.upload',
            headers=headers,
            data=body,
            files=files
        ).json()

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
                                            bigemoji_pk,
                                            token_pk
                                        ])
        else:
            requests.post(response_url, json={
                'response_type': 'ephemeral',
                'text': 'Something went wrong. Please try again!'
            })
    except (BigEmoji.DoesNotExist, SlackToken.DoesNotExist, ValueError):
        requests.post(response_url, json={
            'response_type': 'ephemeral',
            'text': 'Something went wrong. Please try again!'
        })


@shared_task
def delete_bigemoji(channel_id, timestamp, file_id, bigemoji_pk, token_pk):
    from ..models import BigEmoji
    from .models import SlackToken

    try:
        bigemoji = BigEmoji.objects.get(pk=bigemoji_pk)
        token = SlackToken.objects.get(pk=token_pk)

        headers = {
            'Authorization': 'Bearer {}'.format(token.token)
        }

        requests.post(
            'https://slack.com/api/chat.update',
            headers=headers,
            data={
                'channel': channel_id,
                'text': '[BigEmoji:{}]'.format(bigemoji.emoji_name),
                'ts': timestamp,
                'as_user': True
            }
        )

        requests.post(
            'https://slack.com/api/files.delete',
            headers=headers,
            data={
                'file': file_id
            }
        )
    except (BigEmoji.DoesNotExist, SlackToken.DoesNotExist, ValueError):
        pass
