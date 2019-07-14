from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import JsonResponse, HttpResponse

import shlex

from slackauth.decorators import slack_request
from .tasks import upload_bigemoji, bigemoji_list


@require_POST
@slack_request
def index(request):
    cmd = request.POST.get('command')
    cmd_args = shlex.split(request.POST.get('text'))
    slack_user_id = request.POST.get('user_id')
    team_id = request.POST.get('team_id')
    channel_id = request.POST.get('channel_id')
    response_url = request.POST.get('response_url')

    commands = settings.BIGEMOJI_SLACKAPP_COMMANDS
    if cmd in commands.get('bigemoji'):
        if len(cmd_args) == 1:
            bigemoji_name = cmd_args[0]
            upload_bigemoji.delay(team_id, channel_id, slack_user_id, bigemoji_name, response_url)
            return HttpResponse()
        else:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': 'The command should contain exactly 1 argument.'
            })
    elif cmd in commands.get('bigemoji_list'):
        bigemoji_list.delay(team_id, response_url)
        return HttpResponse()
    else:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': 'Unknown command!'
        })
