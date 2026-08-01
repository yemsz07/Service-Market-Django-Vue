
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authentication import CustomJWTAuthentication
from ..models import Product, Service
from ..serializers import ProductSerializer, ServiceSerializer


# ==========================================
# 🛒 4. BUY AND SELL MARKET (Marketplace)
# ==========================================

@api_view(['GET']) # <-- GET na lang, tinanggal na ang POST!
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated]) # o AllowAny kung pwedeng makakita kahit 'di naka-login
def buyandsell_list(request):
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


# =======================================    
# 🛠️ SERVICE LIST
# =======================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])  # 🔒 In-add ang JWT Cookie Check
@permission_classes([IsAuthenticated])              # 🔒 Require login
def service_list(request):
    """
    Returns a list of all available services.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER service_list() ====================")
    print(f"🐍 [DJANGO VIEW] Request method: {request.method}")

    services = Service.objects.all().order_by('-created_at')
    print(f"🐍 [DJANGO VIEW] Fetched services queryset count: {services.count()}")

    # 💡 Sinamahan ng context={'request': request} para sa full image URLs
    serializer = ServiceSerializer(services, many=True, context={'request': request})
    print(f"🐍 [DJANGO VIEW] Serialized data count: {len(serializer.data)}")

    print("🐍 [DJANGO VIEW] ==================== EXIT service_list() ====================")
    return Response(serializer.data, status=status.HTTP_200_OK)