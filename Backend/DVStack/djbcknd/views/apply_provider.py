# ===============================================
# 📦 IMPORTS
# ===============================================
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authentication import CustomJWTAuthentication
from ..models import Profile, ServiceProviderProfile
from ..serializers import UserProfileStatusSerializer


# ===============================================
# 📝 APPLY AS PROVIDER
# ===============================================
@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def apply_as_provider(request):
    """
    Pinapayagan ang user na mag-submit ng verification requirements (ID & Address).
    """
    # Safe lookup para iwas AttributeError kung walang profile instance
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Check kung may existing application na
    provider_profile, created = ServiceProviderProfile.objects.get_or_create(profile=profile)
    
    if provider_profile.approval_status == 'APPROVED':
        return Response({'message': 'Verified provider ka na!'}, status=status.HTTP_400_BAD_REQUEST)

    if provider_profile.approval_status == 'PENDING':
        return Response({'message': 'Naisumite na ang iyong application. Kasalukuyan pa itong nire-rebyu ng Admin.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Kunin ang uploaded files at text
    valid_id = request.FILES.get('valid_id')
    provider_avatar = request.FILES.get('provider_avatar')
    detailed_address = request.data.get('detailed_address')

    if not valid_id or not detailed_address or not provider_avatar:
        return Response({'error': 'Kailangan ang Valid ID, Avatar, at Detailed Address.'}, status=status.HTTP_400_BAD_REQUEST)

    provider_profile.valid_id = valid_id
    provider_profile.provider_avatar = provider_avatar
    provider_profile.detailed_address = detailed_address
    provider_profile.approval_status = 'PENDING'  # I-set sa Pending
    provider_profile.save()

    return Response({'message': 'Naisumite na ang iyong application! Hintayin ang rebyu ng Admin.'}, status=status.HTTP_200_OK)


# ===============================================
# 🔎 CHECK PROVIDER STATUS
# ===============================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def check_provider_status(request):
    """
    Kinukuha ang approval_status ng kasalukuyang naka-login na user.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    serializer = UserProfileStatusSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)