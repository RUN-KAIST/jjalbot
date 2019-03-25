import requests


def slack_delayed_response(response_url, message, response_type='ephemeral'):
    requests.post(response_url, json={
        'response_type': response_type,
        'text': message
    })


def slack_api_call(method, token, **kwargs):
    files = None
    if method == 'files.upload':
        files = {'file': kwargs.pop('file')} if 'file' in kwargs else None

    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }

    return requests.post(
        'https://slack.com/api/{}'.format(method),
        headers=headers,
        data=kwargs,
        files=files
    ).json()
