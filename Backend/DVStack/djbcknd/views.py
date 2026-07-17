# File: djbcknd/views.py
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.response import Response
from .models import Product, Service, User
from .serializers import ProductSerializer, ServiceSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .authentication import CustomJWTAuthentication


@api_view(['GET'])
def service_list(request):
    try:
        service = Service.objects.all()
        serializer = ServiceSerializer(service, many=True)
        return Response(serializer.data)
    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)


@api_view(['GET'])
def buyandsell_list(request):
    try:
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


@api_view(['POST'])
@authentication_classes([])
def login(request):

    username = request.data.get('username')
    password = request.data.get('password')


    print(f"DEBUG DATA -> Username: {username}, Password: {password}")

    if not username or not password:
        return Response(
            {
                "message": "Username and password are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is not None:

        refresh = RefreshToken.for_user(user)

        response = Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.username
        }, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=3600
        )

        return response
    else:
        return Response(
            {"detail": "Your Username or Password are wrong please try again."},
            status=status.HTTP_401_UNAUTHORIZED 
        )


@api_view(['POST'])
@authentication_classes([])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    print(f"DEBUG DATA -> Username: {username}, Password: {password}, Email: {email}")

    if not username or not password or not email:
        return Response(
            {
                "message": "Username, password, and email are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(Q(username=username) | Q(email=email)).exists():
        return Response(
            {
                "message": "Username or email already exists"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save() 
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)

    else:
        return Response({
            "message": "User creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
@authentication_classes([])
def logout(request):
    response = Response({
        "message": "Logout successful"
    })
    response.delete_cookie("access_token")
    return response

