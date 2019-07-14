from django.views.decorators.http import require_POST
from django.http import HttpResponse

import json
import logging

from slackauth.decorators import slack_request
from .tasks import handle_message


logger = logging.getLogger(__name__)


@require_POST
@slack_request
def slack_index(request):
    req = json.loads(request.body)
    req_type = req.get('type')
    if req_type == 'url_verification':
        return HttpResponse(req.get('challenge'))
    elif req_type == 'event_callback':
        event_type = req.get('event').get('type')
        if event_type == 'message':
            handle_message.delay(req)
            return HttpResponse()
        else:
            logger.info('Unhandled Slack event')
    else:
        logger.info('Unhandled Slack request type')
    return HttpResponse()
