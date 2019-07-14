from django.urls import path, include
from . import views


app_name = 'chatbot'
urlpatterns = [
    path('slack/', views.slack_index, name='slack_index')
]
