# chatapp/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/direct/(?P<target_user_id>\d+)/$', consumers.DirectMessageConsumer.as_asgi()),
]