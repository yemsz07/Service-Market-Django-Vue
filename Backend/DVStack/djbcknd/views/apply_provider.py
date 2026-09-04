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
# � SECURITY HELPER FUNCTIONS
# ===============================================

def is_valid_image(file):
    """
    Security validation for uploaded image files.
    Prevents script uploads and ensures only valid image files are accepted.
    
    Returns: (is_valid, error_message)
    """
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if file.size > max_size:
        return False, f'File size must be less than 5MB. Current size: {file.size / (1024*1024):.2f}MB'
    
    # Check content type
    if not file.content_type.startswith('image/'):
        return False, f'Invalid file type. Expected image/*, got {file.content_type}'
    
    # Check file extension
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    file_extension = file.name.split('.')[-1].lower() if '.' in file.name else ''
    
    if file_extension not in allowed_extensions:
        return False, f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}. Got: {file_extension}'
    
    return True, None


# ===============================================
# � APPLY AS PROVIDER
# ===============================================
@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def apply_as_provider(request):
    """
    Pinapayagan ang user na mag-submit ng verification requirements (ID & Address).
    Best Practice: Allow image updates even when PENDING if images are missing
    """
    # Logging: Debug received data
    print(f"[PROVIDER APP] request.FILES keys: {list(request.FILES.keys())}")
    print(f"[PROVIDER APP] request.data keys: {list(request.data.keys())}")
    print(f"[PROVIDER APP] valid_id: {request.FILES.get('valid_id')}")
    print(f"[PROVIDER APP] provider_avatar: {request.FILES.get('provider_avatar')}")
    print(f"[PROVIDER APP] detailed_address: {request.data.get('detailed_address')}")
    
    # Safe lookup para iwas AttributeError kung walang profile instance
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Check kung may existing application na
    provider_profile, created = ServiceProviderProfile.objects.get_or_create(profile=profile)
    
    # Only block if APPROVED - cannot re-apply once approved
    if provider_profile.approval_status == 'APPROVED':
        return Response({
            'error': 'ALREADY_APPROVED',
            'message': 'Verified provider ka na!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Allow PENDING users to update their application if images are missing
    # Only block if PENDING AND both images are already present
    if provider_profile.approval_status == 'PENDING':
        if provider_profile.valid_id and provider_profile.provider_avatar:
            return Response({
                'error': 'ALREADY_PENDING',
                'message': 'Naisumite na ang iyong application. Kasalukuyan pa itong nire-rebyu ng Admin.'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Allow update - images are missing
            print(f"[PROVIDER APP] PENDING status but missing images - allowing update")
        
    # Kunin ang uploaded files at text
    valid_id = request.FILES.get('valid_id')
    provider_avatar = request.FILES.get('provider_avatar')
    detailed_address = request.data.get('detailed_address')

    # Best Practice: Detailed validation with specific error messages
    errors = {}
    
    # Validate valid_id image
    if not valid_id:
        errors['valid_id'] = 'Valid ID is required. Please upload a clear image of your government-issued ID.'
    else:
        is_valid, error_msg = is_valid_image(valid_id)
        if not is_valid:
            errors['valid_id'] = error_msg
    
    # Validate provider_avatar image
    if not provider_avatar:
        errors['provider_avatar'] = 'Provider avatar is required. Please upload a profile picture.'
    else:
        is_valid, error_msg = is_valid_image(provider_avatar)
        if not is_valid:
            errors['provider_avatar'] = error_msg
    
    # Validate detailed_address
    if not detailed_address:
        errors['detailed_address'] = 'Detailed address is required. Please provide your complete address.'
    elif len(detailed_address.strip()) < 10:
        errors['detailed_address'] = 'Address must be at least 10 characters long.'
    
    if errors:
        print(f"[PROVIDER APP] Validation errors: {errors}")
        return Response({
            'error': 'VALIDATION_ERROR',
            'details': errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # Save the application
    try:
        # Only update fields if new values are provided
        if valid_id:
            provider_profile.valid_id = valid_id
        if provider_avatar:
            provider_profile.provider_avatar = provider_avatar
        if detailed_address:
            provider_profile.detailed_address = detailed_address.strip()
        
        # Set to PENDING if not already set
        if provider_profile.approval_status != 'PENDING':
            provider_profile.approval_status = 'PENDING'
        
        provider_profile.save()

        print(f"[PROVIDER APP] Application saved successfully for user {request.user.username}")
        return Response({
            'message': 'Naisumite na ang iyong application! Hintayin ang rebyu ng Admin.',
            'status': 'PENDING'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"[PROVIDER APP] Server error: {e}")
        return Response({
            'error': 'SERVER_ERROR',
            'message': 'Failed to save application. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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