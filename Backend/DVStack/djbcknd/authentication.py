from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 🔧 CHANGED: tinanggal ang 'jwt' cookie fallback (hindi naman ginagamit sa login view,
        # linisin para walang unexpected na ibang parte ng system na sumingit dito)
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token