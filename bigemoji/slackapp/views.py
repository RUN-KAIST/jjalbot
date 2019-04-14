from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse

import hmac
import hashlib
import shlex

from .tasks import upload_bigemoji, bigemoji_list


def verify_request(request):
    version = 'v0'
    signing_secret = settings.SLACK_APP_SIGNING_SECRET
    x_slack_request_timestamp = request.META.get('HTTP_X_SLACK_REQUEST_TIMESTAMP', '')
    x_slack_signature = request.META.get('HTTP_X_SLACK_SIGNATURE', '')
    request_body = request.body.decode()
    base_string = '{}:{}:{}'.format(version, x_slack_request_timestamp, request_body)
    verifier = '{}={}'.format(version, hmac.new(signing_secret.encode(),
                                                base_string.encode(),
                                                hashlib.sha256).hexdigest())
    return hmac.compare_digest(verifier, x_slack_signature)


@csrf_exempt
@require_POST
def index(request):
    if verify_request(request):
        cmd = request.POST.get('command')
        cmd_args = shlex.split(request.POST.get('text'))
        slack_user_id = request.POST.get('user_id')
        team_id = request.POST.get('team_id')
        channel_id = request.POST.get('channel_id')
        response_url = request.POST.get('response_url')

        if cmd in ['/bigemoji', '/jjalbot', '/jtest']:
            if len(cmd_args) == 1:
                bigemoji_name = cmd_args[0]
                upload_bigemoji.delay(team_id, channel_id, slack_user_id, bigemoji_name, response_url)
                return HttpResponse()
            else:
                return JsonResponse({
                    'response_type': 'ephemeral',
                    'text': 'The command should contain exactly 1 argument.'
                })
        elif cmd in ['/bigemoji_list', '/jjallist', '/jltest']:
            bigemoji_list.delay(team_id, response_url)
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()