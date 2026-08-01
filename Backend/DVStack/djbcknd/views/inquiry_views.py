# ===============================================
# 📦 IMPORTS
# ===============================================
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..authentication import CustomJWTAuthentication
from ..models import Service, ServiceInquiry
from ..serializers import ServiceInquirySerializer


# ===============================================
# 📩 1. CREATE INQUIRY
# ===============================================
@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def create_inquiry(request):
    """
    Ginagamit ng CLIENT para magpadala ng bagong inquiry sa isang Service.
    """
    service_id = request.data.get('service')
    message = request.data.get('message')

    if not service_id or not message:
        return Response(
            {"error": "Kailangan ang service at message."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response(
            {"error": "Hindi natagpuan ang service."},
            status=status.HTTP_404_NOT_FOUND
        )

    inquiry = ServiceInquiry.objects.create(
        client=request.user,
        service=service,
        message=message
    )

    serializer = ServiceInquirySerializer(inquiry, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ===============================================
# 📊 2. PORTAL DASHBOARD INQUIRIES
# ===============================================
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_inquiries(request):
    """
    Fetches inquiries for logged-in user.
    """
    print("🐍 [DJANGO VIEW] ==================== ENTER get_inquiries() ====================")
    print(f"🐍 [DJANGO VIEW] request.user: {request.user}")

    # Kinukuha ang inquiries kung saan ang logged-in user ang may-ari ng Service
    inquiries = ServiceInquiry.objects.filter(
        service__provider__profile__user=request.user
    ).order_by('-created_at')

    print(f"🐍 [DJANGO VIEW] inquiries queryset -> Type: {type(inquiries)} | Count: {inquiries.count()}")

    serializer = ServiceInquirySerializer(inquiries, many=True, context={'request': request})
    print(f"🐍 [DJANGO VIEW] Serialized data type: {type(serializer.data)} | Length: {len(serializer.data)}")
    
    if len(serializer.data) > 0:
        print(f"🐍 [DJANGO VIEW] Sample item keys: {list(serializer.data[0].keys())}")

    print("🐍 [DJANGO VIEW] ==================== EXIT get_inquiries() [200] ====================")
    return Response(serializer.data, status=status.HTTP_200_OK)