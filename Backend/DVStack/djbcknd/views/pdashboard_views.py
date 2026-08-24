# ===============================================
# 📦 IMPORTS FOR PRODUCTS.PY
# ===============================================
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
# 📦 PRODUCT VIEWSET (Public Browsing & Seller Filtering)
# ==========================================
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for products.
    Allows public reading (GET) and requires authentication for mutating data (POST, PUT, DELETE).
    """
    serializer_class = ProductSerializer
    authentication_classes = [CustomJWTAuthentication]
    # 🟢 TAMA: AllowAnyReadOnly para mabasa ng kahit sino, pero IsAuthenticated kapag magpo-post/edit
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        # 🟢 Optimization + Safety Check
        queryset = Product.objects.select_related('seller__user').prefetch_related('images').all()

        # Kung may query param na ?mine=true, saka lang i-filter sa sariling items ng user
        if self.request.query_params.get('mine') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(seller__user=self.request.user)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
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