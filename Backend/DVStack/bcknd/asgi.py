"""
ASGI config for bcknd project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

"""
ASGI config for bcknd project.
"""

# bcknd/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bcknd.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import CookieMiddleware, SessionMiddleware
from chatapp.middleware import JWTAuthMiddlewareStack
import chatapp.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CookieMiddleware(
        SessionMiddleware(
            JWTAuthMiddlewareStack(
                URLRouter(
                    chatapp.routing.websocket_urlpatterns
                )
            )
        )
    ),
})