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
        # TODO: Change user to uid, receiving from user form
        account = SocialAccount.objects.filter(provider='slack',
                                               user=request.user)[0:1].get()
        team_id = account.uid.split('_')[0]

        if request.method == 'POST':
            bigemoji = BigEmoji(author=account, team_id=team_id)
            form = BigEmojiForm(request.POST, request.FILES, instance=bigemoji)
            form.save()
            return HttpResponseRedirect(reverse('bigemoji:index'))

        empty_form = BigEmojiForm()
        bigemojis = BigEmoji.objects.filter(team_id=team_id).order_by('-date_created')

        return render(request, 'bigemoji/index.html', {
            'form': empty_form,
            'bigemojis': bigemojis,
        })

    except (SocialAccount.DoesNotExist, ValueError):
        return HttpResponseNotFound()
