from ninja.security import HttpBearer
from djbcknd.authentication import CustomJWTAuthentication


class CustomJWTAuth(HttpBearer):
    def authenticate(self, request, token):
        # I-attach ang Bearer token sa HTTP headers para mabasa ng DRF authenticator
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"

        authenticator = CustomJWTAuthentication()
        try:
            auth_result = authenticator.authenticate(request)
            if auth_result is not None:
                user, _ = auth_result

                if user and user.is_active:
                    request.user = user
                    return user
            return None
        except Exception:
            return None

    def __call__(self, request):
        # Check for Bearer token in Authorization header first
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            return self.authenticate(request, token)
        
        # Fallback: check for access_token cookie (same as main app authentication)
        cookie_token = request.COOKIES.get('access_token')
        if cookie_token:
            request.META['HTTP_AUTHORIZATION'] = f"Bearer {cookie_token}"
            authenticator = CustomJWTAuthentication()
            try:
                auth_result = authenticator.authenticate(request)
                if auth_result is not None:
                    user, _ = auth_result
                    if user and user.is_active:
                        request.user = user
                        return user
            except Exception:
                pass
        
        return None
