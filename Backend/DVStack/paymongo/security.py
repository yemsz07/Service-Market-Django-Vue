from ninja.security import HttpBearer

from djbcknd.authentication import CustomJWTAuthentication


class CustomJWTAuth(HttpBearer):
    """
    Ninja authentication class na compatible sa cookie-based CustomJWTAuthentication.

    Sinusuportahan ang dalawang entry point:
      1. Authorization: Bearer <token>  (header)
      2. access_token=<token>            (cookie — ginagamit ng Vue frontend)

    Sa parehong kaso, ang token ay inilalagay sa request.COOKIES['access_token']
    dahil doon nagbabasa ang CustomJWTAuthentication.
    """

    def authenticate(self, request, token):
        # Ilagay ang token sa COOKIES — doon nagbabasa ang DRF authenticator
        request.COOKIES['access_token'] = token

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
        # 1) Header path — Authorization: Bearer <token>
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            return self.authenticate(request, token)

        # 2) Cookie path — access_token=<token>
        # Reuse ang authenticate() para isang logic lang
        cookie_token = request.COOKIES.get('access_token')
        if cookie_token:
            return self.authenticate(request, cookie_token)

        return None