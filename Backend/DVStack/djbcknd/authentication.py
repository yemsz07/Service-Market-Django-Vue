
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Kukunin natin ang token mula sa cookie sa halip na sa Authorization header
        raw_token = request.COOKIES.get('access_token') or request.COOKIES.get('jwt') # palitan ang pangalan depende sa gamit mo

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token