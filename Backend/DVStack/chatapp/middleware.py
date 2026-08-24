# chatapp/middleware.py
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt

User = get_user_model()

class JWTAuthMiddleware:
    """
    Custom middleware to authenticate WebSocket connections using JWT from HttpOnly cookie.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Try to get the access_token from cookies
        cookies = scope.get('headers', {})
        access_token = None
        
        for header_name, header_value in cookies:
            if header_name.decode('utf-8') == 'cookie':
                cookie_str = header_value.decode('utf-8')
                # Parse cookies
                for cookie in cookie_str.split(';'):
                    cookie = cookie.strip()
                    if cookie.startswith('access_token='):
                        access_token = cookie.split('=')[1]
                        break
        
        if access_token:
            try:
                # Decode JWT token
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                
                if user_id:
                    # Get user from database
                    scope['user'] = await database_sync_to_async(User.objects.get)(id=user_id)
                else:
                    scope['user'] = None
            except Exception as e:
                print(f"[JWT Middleware] Error decoding token: {e}")
                scope['user'] = None
        else:
            scope['user'] = None
        
        return await self.inner(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
