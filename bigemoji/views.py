from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse

from .forms import BigEmojiForm
from .models import BigEmoji
from .slack.models import SlackAccount, SlackTeam


@login_required
def index(request):
    try:
        request_uid = request.GET.get('uid', '_')
        team_id, slack_user_id = request_uid.split('_')
        account_set = SlackAccount.objects.filter(account__user=request.user)
        try:
            team = SlackTeam.objects.get(pk=team_id)
            account = account_set.get(team=team, slack_user_id=slack_user_id)
        except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist):
            account = account_set[0:1].get()

        team_id, slack_user_id = account.team.id, account.slack_user_id
        return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team_id, slack_user_id)))

    except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist, ValueError):
        return HttpResponseNotFound()


@login_required
def bigemoji(request, team_id, slack_user_id):
    try:
        team = SlackTeam.objects.get(pk=team_id)
        account_set = SlackAccount.objects.filter(account__user=request.user)
        account = account_set.get(team=team, slack_user_id=slack_user_id)

        if request.method == 'POST':
            bigemoji = BigEmoji(owner=account, team=team)
            form = BigEmojiForm(request.POST, request.FILES, instance=bigemoji)
            form.save()
            return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team.id, slack_user_id)))

        empty_form = BigEmojiForm()
        bigemojis = BigEmoji.objects.filter(team_id=team.id).order_by('-date_created')

        return render(request, 'bigemoji/index.html', {
            'form': empty_form,
            'account_set': account_set,
            'account_user': account,
            'team_id': team.id,
            'bigemojis': bigemojis,
        })

    except (SlackTeam.DoesNotExist, SlackAccount.DoesNotExist, ValueError):
        return HttpResponseNotFound()
