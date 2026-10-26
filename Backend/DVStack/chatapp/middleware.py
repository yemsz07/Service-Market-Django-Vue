# chatapp/middleware.py
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()


# ==========================================
# 🌐 HTTP MIDDLEWARE — PRESENCE TRACKING
# ==========================================

class PresenceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            try:
                from chatapp.presence import mark_user_online
                mark_user_online(user.id)
                print(f"[PRESENCE] Updated last_seen for: {user.username}")   # ← debug
            except Exception as e:
                print(f"[PRESENCE] ERROR: {type(e).__name__}: {e}") 


# ==========================================
# 🔌 WEBSOCKET MIDDLEWARE — JWT AUTH
# ==========================================

class JWTAuthMiddleware:
    """
    Custom middleware to authenticate WebSocket connections using JWT from HttpOnly cookie.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        access_token = None

        headers = dict(scope.get('headers', []))
        cookie_header = headers.get(b'cookie', b'').decode('utf-8')

        if cookie_header:
            for cookie in cookie_header.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('access_token='):
                    access_token = cookie.split('=', 1)[1].strip()
                    break

        scope['user'] = AnonymousUser()

        if access_token:
            try:
                validated_token = AccessToken(access_token)
                user_id = validated_token.get('user_id')

                if user_id:
                    try:
                        scope['user'] = await database_sync_to_async(User.objects.get)(id=user_id)
                    except User.DoesNotExist:
                        scope['user'] = AnonymousUser()
            except (TokenError, InvalidToken):
                scope['user'] = AnonymousUser()
            except Exception as e:
                print(f"[JWT Middleware] Unexpected error: {e}")
                scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))