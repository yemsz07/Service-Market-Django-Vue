"""
Views configuration for djbcknd app.
Handles authentication, products, services, and seller dashboard requests.
"""

# ==========================================
# 📦 1. IMPORTS (Preparing our tools)
# ==========================================

import logging  # 📜 Logger: Used to record errors or events happening in the background.

from django.contrib.auth import authenticate  # 💂 Guard: Checks if username & password match.
from django.db.models import Q  # 🪄 Query Tool: Used for "OR" logic (e.g., search by Username OR Email).
from rest_framework import status, viewsets  # 🚦 Status Codes (200, 400) & Ready-made ViewSets.
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # 🚪 Route Decorators.
from rest_framework.permissions import IsAuthenticated  # 👮 Police: Blocks unauthenticated users.
from rest_framework.response import Response  # 🎁 Response: The JSON data returned to Frontend/Vue.
from rest_framework_simplejwt.tokens import RefreshToken  # 🎟️ JWT Token generator.

from .authentication import CustomJWTAuthentication  # 🔎 Reads the JWT token inside HttpOnly cookies.
from .models import Product, Profile, Service, User  # 🧸 Database Models.
from .serializers import ProductSerializer, ServiceSerializer, UserSerializer  # 🗣️ Translators (Django Objects to JSON).

logger = logging.getLogger(__name__)


# ==========================================
# 🧸 2. PRODUCT VIEWSET (VIP Store)
# ==========================================

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products belonging exclusively to the authenticated user.
    """
    serializer_class = ProductSerializer  # 🗣️ Uses ProductSerializer for validation & structure.
    permission_classes = [IsAuthenticated]  # 👮 Only logged-in users can access.

    def get_serializer_context(self):
        """
        Passes the request context to the serializer so it can build complete Image URLs.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        """
        Fetches ONLY products created by the current user, ordered newest first.
        """
        return Product.objects.filter(seller__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Before saving: Safely fetches or creates the user's Profile, then links it to the Product.
        """
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        serializer.save(seller=profile)


# ==========================================
# 🛠️ 3. SERVICE LIST (Public Services)
# ==========================================

@api_view(['GET'])  # 🚪 Only allows GET requests (reading data).
def service_list(request):
    """
    Returns a list of all available services.
    """
    services = Service.objects.all()  # 🧺 Fetch all service records.
    serializer = ServiceSerializer(services, many=True)  # 🗣️ Serialize to JSON format.
    return Response(serializer.data)  # 🎁 Send response to client.


# ==========================================
# 🛒 4. BUY AND SELL MARKET (Marketplace)
# ==========================================

@api_view(['GET', 'POST'])  # 🚪 Allows both GET (viewing) and POST (creating) items.
@authentication_classes([CustomJWTAuthentication])  # 🔎 Authenticates via HttpOnly cookie.
@permission_classes([IsAuthenticated])  # 👮 Requires valid login session.
def buyandsell_list(request):
    """
    GET: Retrieves all products in the marketplace.
    POST: Creates a new product under the authenticated seller.
    """
    # 🟢 IF VIEWING ALL PRODUCTS ('GET'):
    if request.method == 'GET':
        products = Product.objects.all().order_by('-created_at')  # 📦 Get all items, latest first.
        serializer = ProductSerializer(products, many=True, context={'request': request})  # 🗣️ Serialize with image URLs.
        return Response(serializer.data)  # 🎁 Return list of products.
        
    # 🔴 IF CREATING A NEW PRODUCT ('POST'):
    elif request.method == 'POST':
        profile, _ = Profile.objects.get_or_create(user=request.user)  # 🏷️ Ensure Profile exists.
        serializer = ProductSerializer(data=request.data, context={'request': request})  # 📝 Parse incoming data.
        
        # 🟢 IF DATA IS VALID:
        if serializer.is_valid():
            user_city = profile.city if profile.city else 'Unknown'  # 🏙️ Default city if empty.
            product = serializer.save(seller=profile, city=user_city)  # 💾 Save product to DB.
            
            response_serializer = ProductSerializer(product, context={'request': request})  # 🗣️ Re-serialize with full URLs.
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)  # 🚦 201 Created Status.
            
        # 🔴 IF DATA IS INVALID:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 🚦 400 Bad Request Status.


# ==========================================
# 🔑 5. LOGIN (Authentication Entrance)
# ==========================================

@api_view(['POST'])  # 🚪 Public endpoint for user login.
@authentication_classes([])  # 🔓 No authentication needed to log in.
def login(request):
    """
    Authenticates user and returns JWT token alongside HttpOnly cookie.
    """
    username = request.data.get('username')  # 🗣️ Extract username from request body.
    password = request.data.get('password')  # 🗣️ Extract password from request body.

    # 🔴 IF MISSING FIELDS:
    if not username or not password:
        return Response(
            {"message": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)  # 💂 Check credentials against DB.

    # 🟢 IF CREDENTIALS ARE VALID:
    if user is not None:
        refresh = RefreshToken.for_user(user)  # 🎟️ Generate JWT token pair.

        response = Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.username
        }, status=status.HTTP_200_OK)  # 🟢 200 OK Status.

        # 🕵️ Store Access Token inside an HttpOnly cookie for security:
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=3600
        )

        return response
    
    # 🔴 IF CREDENTIALS ARE INVALID:
    else:
        return Response(
            {"detail": "Your Username or Password are wrong please try again."},
            status=status.HTTP_401_UNAUTHORIZED  # 🚦 401 Unauthorized Status.
        )


# ==========================================
# 📝 6. REGISTER (User Account Creation)
# ==========================================

@api_view(['POST'])  # 🚪 Public endpoint for registration.
@authentication_classes([])  # 🔓 No authentication needed.
def register(request):
    """
    Registers a new user account.
    """
    username = request.data.get('username')  # 🗣️ Get username.
    password = request.data.get('password')  # 🗣️ Get password.
    email = request.data.get('email')        # 🗣️ Get email.

    # 🔴 IF MISSING REQUIRED FIELDS:
    if not username or not password or not email:
        return Response(
            {"message": "Username, password, and email are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔴 IF USERNAME OR EMAIL ALREADY TAKEN:
    if User.objects.filter(Q(username=username) | Q(email=email)).exists():
        return Response(
            {"message": "Username or email already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = UserSerializer(data=request.data)  # 📝 Validate payload using UserSerializer.

    # 🟢 IF VALIDATION PASSED:
    if serializer.is_valid():
        user = serializer.save()  # 💾 Create new user record in DB.
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)  # 🚦 201 Created Status.
    
    # 🔴 IF VALIDATION FAILED:
    else:
        return Response({
            "message": "User creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
    # 🟢 Return current user details if valid:
    return Response({
        "authenticated": True,
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        }
    })


# ==========================================
# 🚪 8. LOGOUT (Session Termination)
# ==========================================

@api_view(['POST'])  # 🚪 Post request to logout.
@authentication_classes([])
def logout(request):
    """
    Logs out user by deleting the access token cookie.
    """
    response = Response({"message": "Logout successful"})
    response.delete_cookie("access_token")  # 🗑️ Remove HttpOnly cookie from client browser.
    return response


# ==========================================
# 📊 9. GET ITEMS FOR SALE (Count User Products)
# ==========================================

@api_view(['GET'])  # 🚪 Protected endpoint to fetch product count.
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_items_for_sale(request):
    """
    Counts total items for sale by logged-in user.
    """
    items_for_sale = Product.objects.filter(seller__user=request.user).count()  # 🔢 Count total active listings.
    return Response({"items_for_sale": items_for_sale})  # 🎁 Return total integer count.


# ==========================================
# 🏠 10. PORTAL DASHBOARD (Seller Dashboard)
# ==========================================

@api_view(['GET'])  # 🚪 Protected dashboard endpoint.
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def portal_dashboard(request):
    """
    Fetches products owned specifically by logged-in seller for portal display.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)  # 🏷️ Ensure Profile exists.
    my_products = Product.objects.filter(seller=profile).order_by('-created_at')  # 📦 Fetch user products (newest first).

    serializer = ProductSerializer(my_products, many=True, context={'request': request})  # 🗣️ Serialize with image URLs.
    return Response(serializer.data)  # 🎁 Return array of product objects.