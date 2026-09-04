# chatapp/routing.py
from django.urls import re_path
from . import consumers
from .notification_consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/direct/(?P<target_user_id>\d+)/$', consumers.DirectMessageConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]