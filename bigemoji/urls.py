from django.urls import path, include
from . import views


app_name = 'bigemoji'
urlpatterns = [
    path('', views.index, name='index'),
    path('bigemoji/<team_id>/<slack_user_id>/', include([
        path('', views.bigemoji_index, name='bigemoji'),
        path('add/', views.bigemoji_add, {'is_alias': False}, name='add'),
        path('alias/', views.bigemoji_add, {'is_alias': True}, name='alias'),
        path('remove/<bigemoji_name>', views.bigemoji_remove, name='remove'),
    ])),
    path('app/', include('bigemoji.slackapp.urls'))
]
