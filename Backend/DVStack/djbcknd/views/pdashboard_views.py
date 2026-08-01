# ===============================================
# 📦 IMPORTS FOR PRODUCTS.PY
# ===============================================
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authentication import CustomJWTAuthentication
from ..models import Product, Profile
from ..serializers import ProductSerializer

# ==========================================
# 🛒 1. PUBLIC MARKETPLACE (Buy & Sell List)
# ==========================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def buyandsell_list(request):
    """
    Kinukuha ang LAHAT ng active products para sa Buy & Sell Marketplace feed.
    """
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 🧸 2. PRODUCT VIEWSET (Seller CRUD)
# ==========================================
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products belonging exclusively to the authenticated user.
    """
    serializer_class = ProductSerializer
    authentication_classes = [CustomJWTAuthentication]  # 🔑 JWT Security check added!
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        print("🐍 [DJANGO VIEW] ---- ENTER ProductViewSet.get_serializer_context() ----")
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        print("🐍 [DJANGO VIEW] ==================== ENTER ProductViewSet.get_queryset() ====================")
        return Product.objects.filter(seller__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        print("🐍 [DJANGO VIEW] ==================== ENTER ProductViewSet.perform_create() ====================")
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        serializer.save(seller=profile)


# ==========================================
# 🏠 3. PORTAL DASHBOARD (Seller Dashboard)
# ==========================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def portal_dashboard(request):
    """
    Fetches products owned specifically by logged-in seller for portal display.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER portal_dashboard() ====================")
    profile, created = Profile.objects.get_or_create(user=request.user)
    my_products = Product.objects.filter(seller=profile).order_by('-created_at')

    serializer = ProductSerializer(my_products, many=True, context={'request': request})
    print("🐍 [DJANGO VIEW] ==================== EXIT portal_dashboard() [200] ====================")
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 📊 4. GET ITEMS FOR SALE (Count User Products)
# ==========================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_items_for_sale(request):
    """
    Counts total items for sale by logged-in user.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER get_items_for_sale() ====================")
    items_for_sale = Product.objects.filter(seller__user=request.user).count()
    print("🐍 [DJANGO VIEW] ==================== EXIT get_items_for_sale() [200] ====================")
    return Response({"items_for_sale": items_for_sale}, status=status.HTTP_200_OK)