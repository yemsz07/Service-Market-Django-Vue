from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken

from ..authentication import CustomJWTAuthentication
from ..serializers import UserSerializer


# Cookie lifetimes — tugma sa SIMPLE_JWT settings
ACCESS_MAX_AGE = 60 * 15              # 15 min  = ACCESS_TOKEN_LIFETIME
REFRESH_MAX_AGE = 60 * 60 * 24 * 7    # 7 days  = REFRESH_TOKEN_LIFETIME
REFRESH_COOKIE_PATH = "/api/"


def _set_auth_cookies(response, access_token, refresh_token=None):
    """I-set ang access (at optional refresh) cookies nang consistent."""
    response.set_cookie(
        key="access_token",
        value=str(access_token),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Strict",
        max_age=ACCESS_MAX_AGE,
        path="/",
    )
    if refresh_token is not None:
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=REFRESH_MAX_AGE,
            path=REFRESH_COOKIE_PATH,  # limitado sa refresh endpoint
        )


def _clear_auth_cookies(response):
    """I-delete ang parehong cookies (tamang path)."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path=REFRESH_COOKIE_PATH)


# ==========================================
# REGISTER
# ==========================================
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register(request):
    """Registers a new user account safely relying on Serializer validation."""
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "User created successfully",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {
            "message": "User creation failed",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


# ==========================================
# LOGIN
# ==========================================
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def login(request):
    """Authenticate user, issue access + refresh tokens as HttpOnly cookies."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"message": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        # Generic message — anti-enumeration
        return Response(
            {"detail": "Your Username or Password are wrong please try again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    response = Response(
        {
            "message": "Login successful",
            "username": user.username,
        },
        status=status.HTTP_200_OK,
    )
    _set_auth_cookies(response, refresh.access_token, refresh)
    return response


# ==========================================
# REFRESH
# ==========================================
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Rotates refresh token and issues new access token.
    Uses TokenRefreshSerializer so ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION
    actually run (manual RefreshToken() would NOT trigger them).
    """
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return Response(
            {"detail": "No refresh token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
    try:
        serializer.is_valid(raise_exception=True)
    except (TokenError, InvalidToken):
        response = Response(
            {"detail": "Invalid or expired refresh token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
        _clear_auth_cookies(response)
        return response

    data = serializer.validated_data

    response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
    # Kapag ROTATE_REFRESH_TOKENS=True, may bagong 'refresh' sa data
    _set_auth_cookies(response, data["access"], data.get("refresh"))
    return response


# ==========================================
# CHECK AUTH
# ==========================================
@api_view(["GET"])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response(
        {
            "authenticated": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            },
        }
    )


# ==========================================
# LOGOUT
# ==========================================
@api_view(["POST"])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    """Blacklist refresh token (server-side revocation) and clear cookies."""
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass  # expired or invalid ang cookies

    response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    _clear_auth_cookies(response)
    return response