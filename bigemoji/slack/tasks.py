from celery import shared_task
import requests
import re
import os


@shared_task
def upload_bigemoji(channel_id, bigemoji_pk, token_pk, response_url):
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

        resp = requests.post(
            'https://slack.com/api/files.upload',
            headers=headers,
            data=body,
            files=files
        )

        if not resp.json().get('ok'):
            print(resp.json())
            requests.post(response_url, json={
                'response_type': 'ephemeral',
                'text': 'Something went wrong. Please try again!'
            })
    except (BigEmoji.DoesNotExist, SlackToken.DoesNotExist, ValueError):
        requests.post(response_url, json={
            'response_type': 'ephemeral',
            'text': 'Something went wrong. Please try again!'
        })
