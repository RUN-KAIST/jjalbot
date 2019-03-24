from django.urls import path, include
from . import views


app_name = 'bigemoji'
urlpatterns = [
    path('', views.index, name='index'),
    path('bigemoji/<team_id>/<slack_user_id>', views.bigemoji, name='bigemoji'),
    path('app/', include('bigemoji.slack.urls'))
]
