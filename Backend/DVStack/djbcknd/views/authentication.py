from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from ..authentication import CustomJWTAuthentication
from ..serializers import UserSerializer


# ==========================================
# REGISTER
# ==========================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])  # 🔧 CHANGED: explicit na AllowAny (dati wala, pwedeng ma-block ng global default)
@throttle_classes([AnonRateThrottle])  # 🔧 CHANGED: rate-limit para hindi ma-spam ng fake accounts
def register(request):
    """
    Registers a new user account safely relying on Serializer validation.
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "message": "User creation failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# LOGIN
# ==========================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])  # 🔧 CHANGED: explicit na AllowAny
@throttle_classes([AnonRateThrottle])  # 🔧 CHANGED: rate-limit laban sa brute-force login attempts
def login(request):
    """
    Authenticates user and attaches JWT access token to an HttpOnly cookie.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"message": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        response = Response({
            "message": "Login successful",
            "username": user.username
        }, status=status.HTTP_200_OK)

        # Set cookie safely based on environment
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=not settings.DEBUG,  # HTTPS lang sa production
            samesite="Lax",
            max_age=3600
        )
        return response

    return Response(
        {"detail": "Your Username or Password are wrong please try again."},
        status=status.HTTP_401_UNAUTHORIZED
    )


# ==========================================
# CHECK AUTH
# ==========================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({
        "authenticated": True,
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        }
    })


# ==========================================
# LOGOUT
# ==========================================
@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    response = Response({"message": "Logout successful"})
    response.delete_cookie("access_token")
    return response