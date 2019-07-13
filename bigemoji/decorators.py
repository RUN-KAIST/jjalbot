from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

from slackauth.models import SlackAccount, SlackTeam


def slack_login_required(f):
    @wraps(f)
    def wrapper(request, team_id, slack_user_id, *args, **kwargs):
        try:
            team = SlackTeam.objects.get(pk=team_id)
            account_set = SlackAccount.objects.filter(account__user=request.user)
            account = account_set.get(team=team, slack_user_id=slack_user_id)
            return f(request, account, account_set, *args, **kwargs)
        except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist):
            return HttpResponseNotFound()
    return login_required(wrapper)
