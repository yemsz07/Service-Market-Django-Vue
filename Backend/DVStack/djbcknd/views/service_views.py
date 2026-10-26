from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authentication import CustomJWTAuthentication
from ..models import Category
from ..serializers import CategorySerializer, CreateServiceSerializer


# ======================================
# 🏷️ 1. CATEGORIES (For Dropdowns)
# ======================================
class CategoryListView(generics.ListAPIView):
    """
    Returns a list of public categories specifically for Services.
    """
    serializer_class = CategorySerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
         return Category.objects.all()


# ========================================= 
# 📝 2. CREATE SERVICE (Post New Offer)
# ========================================= 
@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def create_service(request):
    user = request.user

    # 1. Check if user has Profile and ServiceProviderProfile
    if not hasattr(user, 'profile') or not hasattr(user.profile, 'service_profile'):
        return Response(
            {"detail": "You need to apply and submit requirements first to become a Service Provider."},
            status=status.HTTP_403_FORBIDDEN
        )

    provider_profile = user.profile.service_profile

    # 2. 🛡️ VERIFICATION CHECK: Is he/she approved by Admin?
    if provider_profile.approval_status != 'APPROVED':
        return Response(
            {
                "detail": "You are not yet allowed to post a Service.",
                "status": provider_profile.approval_status,
                "admin_notes": provider_profile.admin_notes
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # 3. 🟢 KUNG APPROVED: I-process ang creation
    serializer = CreateServiceSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(provider=provider_profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)