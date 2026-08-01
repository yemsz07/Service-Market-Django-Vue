
from ..authentication import CustomJWTAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import UserSerializer



# ==========================================
# 📝 6. REGISTER (User Account Creation)
# ==========================================

@api_view(['POST'])  # 🚪 Public endpoint for registration.
@authentication_classes([])  # 🔓 No authentication needed.
def register(request):
    """
    Registers a new user account.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER register() ====================")
    print(f"🐍 [DJANGO VIEW] Incoming request.data keys: {list(request.data.keys())}")

    username = request.data.get('username')  # 🗣️ Get username.
    password = request.data.get('password')  # 🗣️ Get password.
    email = request.data.get('email')        # 🗣️ Get email.
    print(f"🐍 [DJANGO VIEW] Extracted -> username: {username} | email: {email} | password provided: {'YES' if password else 'NO'}")

    # 🔴 IF MISSING REQUIRED FIELDS:
    if not username or not password or not email:
        print("🐍 [DJANGO VIEW] ❌ Missing required field(s) -> returning 400.")
        print("🐍 [DJANGO VIEW] ==================== EXIT register() [400 missing fields] ====================")
        return Response(
            {"message": "Username, password, and email are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔴 IF USERNAME OR EMAIL ALREADY TAKEN:
    print("🐍 [DJANGO VIEW] 🔎 Checking if username or email already exists...")
    already_exists = User.objects.filter(Q(username=username) | Q(email=email)).exists()
    print(f"🐍 [DJANGO VIEW] already_exists result: {already_exists}")

    if already_exists:
        print("🐍 [DJANGO VIEW] ❌ Username or email already taken -> returning 400.")
        print("🐍 [DJANGO VIEW] ==================== EXIT register() [400 duplicate] ====================")
        return Response(
            {"message": "Username or email already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UserSerializer(data=request.data)  # 📝 Validate payload using UserSerializer.
    print("🐍 [DJANGO VIEW] 🔎 Running UserSerializer.is_valid()...")

    # 🟢 IF VALIDATION PASSED:
    if serializer.is_valid():
        print("🐍 [DJANGO VIEW] ✅ Serializer VALID -> saving user...")
        user = serializer.save()  # 💾 Create new user record in DB.
        print(f"🐍 [DJANGO VIEW] 💾 User created -> id={user.id} | username={user.username}")
        print("🐍 [DJANGO VIEW] ==================== EXIT register() [201 Created] ====================")
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)  # 🚦 201 Created Status.

    # 🔴 IF VALIDATION FAILED:
    else:
        print(f"🐍 [DJANGO VIEW] ❌ Serializer INVALID. Errors: {serializer.errors}")
        print("🐍 [DJANGO VIEW] ==================== EXIT register() [400 validation failed] ====================")
        return Response({
            "message": "User creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



# ==========================================
# 🔑 5. LOGIN (Authentication Entrance)
# ==========================================
  
@api_view(['POST'])  # 🚪 Public endpoint for user login.
@authentication_classes([])  # 🔓 No authentication needed to log in.
def login(request):
    """
    Authenticates user and returns JWT token alongside HttpOnly cookie.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER login() ====================")
    print(f"🐍 [DJANGO VIEW] Incoming request.data keys: {list(request.data.keys())}")

    username = request.data.get('username')  # 🗣️ Extract username from request body.
    password = request.data.get('password')  # 🗣️ Extract password from request body.
    print(f"🐍 [DJANGO VIEW] Extracted username: {username} | password provided: {'YES' if password else 'NO'}")

    # 🔴 IF MISSING FIELDS:
    if not username or not password:
        print("🐍 [DJANGO VIEW] ❌ Missing username or password -> returning 400.")
        print("🐍 [DJANGO VIEW] ==================== EXIT login() [400] ====================")
        return Response(
            {"message": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    print("🐍 [DJANGO VIEW] 🔎 Calling authenticate()...")
    user = authenticate(username=username, password=password)  # 💂 Check credentials against DB.
    print(f"🐍 [DJANGO VIEW] authenticate() result: {'USER FOUND' if user is not None else 'None (invalid credentials)'}")

    # 🟢 IF CREDENTIALS ARE VALID:
    if user is not None:
        print(f"🐍 [DJANGO VIEW] ✅ Credentials valid for user: {user.username} (id={user.id})")
        refresh = RefreshToken.for_user(user)  # 🎟️ Generate JWT token pair.
        print("🐍 [DJANGO VIEW] 🎟️ RefreshToken + AccessToken generated.")

        response = Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.username
        }, status=status.HTTP_200_OK)  # 🟢 200 OK Status.
        print("🐍 [DJANGO VIEW] Response body keys: ['message', 'refresh', 'access', 'username']")

        # 🕵️ Store Access Token inside an HttpOnly cookie for security:
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=3600
        )
        print("🐍 [DJANGO VIEW] 🍪 HttpOnly cookie 'access_token' set (max_age=3600s).")
        print("🐍 [DJANGO VIEW] ==================== EXIT login() [200 OK] ====================")

        return response

    # 🔴 IF CREDENTIALS ARE INVALID:
    else:
        print("🐍 [DJANGO VIEW] ❌ Invalid credentials -> returning 401.")
        print("🐍 [DJANGO VIEW] ==================== EXIT login() [401] ====================")
        return Response(
            {"detail": "Your Username or Password are wrong please try again."},
            status=status.HTTP_401_UNAUTHORIZED  # 🚦 401 Unauthorized Status.
        )


# ==========================================
# 🔍 7. CHECK AUTH (Verify Active Session)
# ==========================================

@api_view(['GET'])  # 🚪 Protected endpoint to verify current auth status.
@authentication_classes([CustomJWTAuthentication])  # 🔎 Validates session via cookie.
@permission_classes([IsAuthenticated])  # 👮 Requires valid session token.
def check_auth(request):
    """
    Verifies if current session token is valid.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER check_auth() ====================")
    print(f"🐍 [DJANGO VIEW] request.user: {request.user} | is_authenticated: {request.user.is_authenticated}")

    payload = {
        "authenticated": True,
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        }
    }
    print(f"🐍 [DJANGO VIEW] Response payload keys: {list(payload.keys())} | user sub-keys: {list(payload['user'].keys())}")
    print("🐍 [DJANGO VIEW] ==================== EXIT check_auth() [200] ====================")

    # 🟢 Return current user details if valid:
    return Response(payload)


# ==========================================
# 🚪 8. LOGOUT (Session Termination)
# ==========================================

@api_view(['POST'])  # 🚪 Post request to logout.
@authentication_classes([IsAuthenticated])
def logout(request):
    """
    Logs out user by deleting the access token cookie.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER logout() ====================")

    response = Response({"message": "Logout successful"})
    response.delete_cookie("access_token")  # 🗑️ Remove HttpOnly cookie from client browser.
    print("🐍 [DJANGO VIEW] 🗑️ 'access_token' cookie deletion instruction added to response.")
    print("🐍 [DJANGO VIEW] ==================== EXIT logout() [200] ====================")

    return response