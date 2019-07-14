from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import BigEmojiForm, BigEmojiAliasForm
from .models import BigEmoji, BigEmojiStorage, BigEmojiFullException
from slackauth.decorators import slack_login_required
from slackauth.models import SlackAccount, SlackTeam


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
def bigemoji_index(request, account, account_set):
    try:
        team = account.team
        if team.verified:
            storage, _ = BigEmojiStorage.objects.get_or_create(defaults={
                'max_size': settings.BIGEMOJI_MAX_SPACE,
                'max_entry': settings.BIGEMOJI_MAX_ENTRY,
                'delete_eta': settings.BIGEMOJI_DELETE_ETA,
            }, team=team)
            empty_add_form = BigEmojiForm()
            empty_alias_form = BigEmojiAliasForm(storage)
            bigemojis = BigEmoji.objects.filter(storage=storage).order_by('-date_created')
        else:
            empty_add_form = BigEmojiForm()
            empty_alias_form = BigEmojiAliasForm(None)
            bigemojis = BigEmoji.objects.none()

        return render(request, 'bigemoji/index.html', {
            'add_form': empty_add_form,
            'alias_form': empty_alias_form,
            'account_set': account_set,
            'account_user': account,
            'team_id': team.id,
            'bigemojis': bigemojis,
        })

    except ValueError:
        return HttpResponseNotFound()


@require_POST
@slack_login_required
def bigemoji_add(request, account, account_set, is_alias):
    try:
        team = account.team

        if team.verified:
            storage = team.bigemojistorage
            bigemoji = BigEmoji(owner=account, storage=storage)
            if is_alias:
                bigemoji = BigEmojiAliasForm(storage, request.POST, instance=bigemoji).save(commit=False)
            else:
                bigemoji = BigEmojiForm(request.POST, request.FILES, instance=bigemoji).save(commit=False)

            try:
                bigemoji.save_emoji()
            except IntegrityError:
                # Django seems to raise an error after it saves the file.
                bigemoji.image_file.delete(save=False)
                messages.add_message(
                    request,
                    messages.ERROR,
                    'A BigEmoji with that name already exists.'
                )
            except BigEmojiFullException:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Your workspace\'s BigEmoji storage is full. Please contact the administrators.'
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'Your workspace is not allowed to use this app. Please contact the administrators.'
            )

        return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team.id, account.slack_user_id)))
    except (BigEmojiStorage.DoesNotExist, ValueError) as e:
        print(e)
        return HttpResponseNotFound()


@require_POST
@slack_login_required
def bigemoji_remove(request, account, account_set, bigemoji_name):
    try:
        team = account.team
        storage = team.bigemojistorage
        bigemoji = BigEmoji.objects.get(storage=storage, emoji_name=bigemoji_name)
        if bigemoji.owner == account:
            bigemoji.delete_emoji()
            messages.add_message(
                request,
                messages.INFO,
                'Successfully deleted BigEmoji {} and its aliases.'.format(bigemoji_name)
            )
            return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team.id, account.slack_user_id)))
        else:
            return HttpResponseNotFound()
    except (BigEmojiStorage.DoesNotExist, BigEmoji.DoesNotExist):
        return HttpResponseNotFound()
