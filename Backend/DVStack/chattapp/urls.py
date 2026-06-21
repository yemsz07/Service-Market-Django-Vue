# chattapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat/history/<str:room_name>/', views.get_chat_history, name='chat_history'),
]
