from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from .forms import BigEmojiForm
from .models import BigEmoji
from allauth.socialaccount.models import SocialAccount


@login_required
def index(request):
    try:
        request_uid = request.GET.get('uid', '')
        account_set = SocialAccount.objects.filter(provider='slack', user=request.user)
        try:
            account = account_set.get(uid=request_uid)
        except SocialAccount.DoesNotExist:
            account = account_set[0:1].get()
        team_id, user_id = account.uid.split('_')
        return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team_id, user_id)))

    except (SocialAccount.DoesNotExist, ValueError):
        return HttpResponseNotFound()


@login_required
def bigemoji(request, team_id, user_id):
    try:
        uid = '{}_{}'.format(team_id, user_id)
        account_set = SocialAccount.objects.filter(user=request.user)
        account = account_set.get(uid=uid)

        if request.method == 'POST':
            bigemoji = BigEmoji(author=account, team_id=team_id)
            form = BigEmojiForm(request.POST, request.FILES, instance=bigemoji)
            form.save()
            return HttpResponseRedirect(reverse('bigemoji:bigemoji', args=(team_id, user_id)))

        empty_form = BigEmojiForm()
        bigemojis = BigEmoji.objects.filter(team_id=team_id).order_by('-date_created')

        return render(request, 'bigemoji/index.html', {
            'form': empty_form,
            'account_set': account_set,
            'account_user': account,
            'bigemojis': bigemojis,
        })

    except (SocialAccount.DoesNotExist, ValueError):
        return HttpResponseNotFound()
