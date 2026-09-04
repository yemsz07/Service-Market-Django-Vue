# chatapp/middleware.py
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
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
        access_token = None
        
        # Headers is a list of tuples: [(b'name', b'value'), ...]
        headers = dict(scope.get('headers', []))
        cookie_header = headers.get(b'cookie', b'').decode('utf-8')
        
        print(f"[JWT Middleware] Cookie header: {cookie_header[:100] if cookie_header else 'None'}...")
        
        # Parse cookies from the cookie header
        if cookie_header:
            for cookie in cookie_header.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('access_token='):
                    access_token = cookie.split('=', 1)[1].strip()
                    print(f"[JWT Middleware] Found access_token")
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
                
                print(f"[JWT Middleware] Decoded token, user_id: {user_id}")
                
                if user_id:
                    # Get user from database
                    try:
                        scope['user'] = await database_sync_to_async(User.objects.get)(id=user_id)
                        print(f"[JWT Middleware] User authenticated: {scope['user'].username}")
                    except User.DoesNotExist:
                        print(f"[JWT Middleware] User {user_id} does not exist")
                        scope['user'] = AnonymousUser()
                else:
                    print(f"[JWT Middleware] No user_id in token")
                    scope['user'] = AnonymousUser()
            except jwt.ExpiredSignatureError:
                print(f"[JWT Middleware] Token expired")
                scope['user'] = AnonymousUser()
            except jwt.InvalidTokenError as e:
                print(f"[JWT Middleware] Invalid token: {e}")
                scope['user'] = AnonymousUser()
            except Exception as e:
                print(f"[JWT Middleware] Error decoding token: {e}")
                import traceback
                traceback.print_exc()
                scope['user'] = AnonymousUser()
        else:
            print(f"[JWT Middleware] No access_token found in cookies")
            scope['user'] = AnonymousUser()
        
        return await self.inner(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
