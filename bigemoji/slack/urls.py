from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path

from . import views
from .provider import SlackProvider


app_name = 'slack'
urlpatterns = [
    path('', views.index, name='index'),
] + default_urlpatterns(SlackProvider)
