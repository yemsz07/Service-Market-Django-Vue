from ninja.security import HttpBearer
from ninja.errors import HttpError
from djbcknd.authentication import CustomJWTAuthentication

class CustomJWTAuth(HttpBearer):
    def authenticate(self, request, token):


        # Lalagyan ng 'Bearer <token>' format para basahin ng DRF/Custom Auth mo
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"
        
        authenticator = CustomJWTAuthentication()
        try:
            # Awtomatikong gagamitin ang iyong custom logic (user lookup, token verification, etc.)
            auth_result = authenticator.authenticate(request)
            
            if auth_result is not None:
                user, validated_token = auth_result
                request.user = user
                return token
            return None
        except Exception:
            return None