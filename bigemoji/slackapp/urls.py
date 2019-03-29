from django.urls import path

from . import views


app_name = 'slackapp'
urlpatterns = [
    path('', views.index, name='index'),
]
