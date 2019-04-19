from django.urls import path

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import SlackProvider
from . import views


urlpatterns = [
    path('slackauth/signup/', views.slack_signup, name='socialaccount_signup')
] + default_urlpatterns(SlackProvider)
