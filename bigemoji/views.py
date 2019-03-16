from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import BigEmojiForm
from .models import BigEmoji
from allauth.socialaccount.models import SocialAccount


@login_required
def index(request):
    empty_form = BigEmojiForm()
    if request.method == 'POST':
        try:
            # TODO: Change user to uid, receiving from user form
            account = SocialAccount.objects.get(provider='slack', user=request.user)

            team_id = account.uid.split('_')[0]
            bigemoji = BigEmoji(author=account, team_id=team_id)
            form = BigEmojiForm(request.POST, request.FILES, instance=bigemoji)
            form.save()
            return HttpResponseRedirect(reverse('bigemoji:index'))

        except SocialAccount.DoesNotExist:
            return render(request, 'bigemoji/index.html', {
                'form': empty_form,
                'error_msg': 'Not a valid account.'
            })
        except ValueError:
            return render(request, 'bigemoji/index.html', {
                'form': empty_form,
                'error_msg': 'Not a valid input.'
            })

    return render(request, 'bigemoji/index.html', {
        'form': empty_form
    })
