from django.urls import path
from . import views


app_name = 'chatbot'
urlpatterns = [
    path('slack/', views.slack_index, name='slack_index')
]
