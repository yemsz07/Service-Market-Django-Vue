# chatapp/middleware.py
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken  # 🔧 CHANGED: gamit na simplejwt, hindi raw jwt
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken  # 🔧 CHANGED

User = get_user_model()

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

        # 🔧 CHANGED: tinanggal ang pag-print ng cookie header — kahit truncated,
        # hindi dapat lumalabas ang token material sa logs

        if cookie_header:
            for cookie in cookie_header.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('access_token='):
                    access_token = cookie.split('=', 1)[1].strip()
                    break

        scope['user'] = AnonymousUser()  # 🔧 CHANGED: default muna bago mag-attempt ng validation

        if access_token:
            try:
                # 🔧 CHANGED: gamit na ang AccessToken mula sa simplejwt — pareho na ang
                # validation logic (signature, expiry, AT ang token_type check) sa REST API mo.
                # Awtomatikong titignan din nito ang blacklist kung naka-enable ang
                # rest_framework_simplejwt.token_blacklist app.
                validated_token = AccessToken(access_token)
                user_id = validated_token.get('user_id')

                if user_id:
                    try:
                        scope['user'] = await database_sync_to_async(User.objects.get)(id=user_id)
                    except User.DoesNotExist:
                        scope['user'] = AnonymousUser()
            except (TokenError, InvalidToken):
                # covers expired, invalid signature, wrong token_type, atbp.
                scope['user'] = AnonymousUser()
            except Exception as e:
                print(f"[JWT Middleware] Unexpected error: {e}")
                scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))