from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_POST

from .decorators import slack_login_required
from .forms import BigEmojiForm
from .models import BigEmoji
from .slack.models import SlackAccountDeprecated as SlackAccount, SlackTeam


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


@slack_login_required
def bigemoji(request, account, account_set):
    try:
        team = account.team
        empty_form = BigEmojiForm()
        bigemojis = BigEmoji.objects.filter(team_id=team.id).order_by('-date_created')

        return render(request, 'bigemoji/index.html', {
            'form': empty_form,
            'account_set': account_set,
            'account_user': account,
            'team_id': team.id,
            'bigemojis': bigemojis,
        })

    except ValueError:
        return HttpResponseNotFound()


@require_POST
@slack_login_required
def bigemoji_add(request, account, account_set):
    team = account.team
    bigemoji = BigEmoji(owner=account, team=team)
    form = BigEmojiForm(request.POST, request.FILES, instance=bigemoji)

    # TODO: Handle race conditions...
    if team.verified and team.occupied() + request.FILES.get('image').size <= team.max_size:
        try:
            form.save()
        except IntegrityError:
            messages.add_message(
                request,
                messages.ERROR,
                'A BigEmoji with that name already exists.'
            )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            'You cannot add BigEmoji to this workspace. Please contact the administrators.'
        )

    return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team.id, account.slack_user_id)))


@require_POST
@slack_login_required
def bigemoji_remove(request, account, account_set, bigemoji_name):
    try:
        team = account.team
        bigemoji = BigEmoji.objects.get(team=team, emoji_name=bigemoji_name)
        if bigemoji.owner == account:
            bigemoji.delete()
            messages.add_message(
                request,
                messages.INFO,
                'Successfully deleted BigEmoji {}.'.format(bigemoji_name)
            )
            return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team.id, account.slack_user_id)))
        else:
            return HttpResponseNotFound()
    except BigEmoji.DoesNotExist:
        return HttpResponseNotFound()
