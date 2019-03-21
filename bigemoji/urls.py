from django.urls import path, include
from . import views


app_name = 'bigemoji'
urlpatterns = [
    path('', views.index, name='index'),
    path('app/', include('bigemoji.slack.urls'))
]
