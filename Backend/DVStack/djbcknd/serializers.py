"""
Serializers configuration for djbcknd app.
Translates Django database models into JSON format (and vice versa) for API requests.
"""

# ==========================================
# 📦 1. IMPORTS (Preparing our tools)
# ==========================================

import logging

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from .models import Category, Product, ProductImage, Service, ServiceInquiry, ServiceProviderProfile, Profile

logger = logging.getLogger(__name__)


# ==========================================
# 🏷️ 2. CATEGORY SERIALIZER
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes Category data into simple JSON.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'slug']


# ==========================================
# 🖼️ 3. PRODUCT IMAGE SERIALIZER
# ==========================================

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Handles individual product images and formats their full URL links.
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_feature', 'uploaded_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


# ==========================================
# 📦 4. PRODUCT SERIALIZER
# ==========================================

class ProductSerializer(serializers.ModelSerializer):
    """
    Main Product Serializer: Handles product details, image upload validations, and primary image resolution.
    """
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    image = serializers.ImageField(
        required=False, 
        write_only=True,
        allow_empty_file=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'city', 'status',
            'category', 'images', 'seller', 'image', 'primary_image'
        ]

    def get_primary_image(self, obj):
        first_img = obj.images.first()
        if first_img and first_img.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_img.image.url)
            return first_img.image.url
        return None

    def create(self, validated_data):
        uploaded_image = validated_data.pop('image', None)
        product = super().create(validated_data)
        
        if uploaded_image:
            try:
                ProductImage.objects.create(product=product, image=uploaded_image, is_feature=True)
            except Exception as e:
                logger.error(f"Failed to create ProductImage for Product ID {product.id}: {e}")
            
        return product


# ==========================================
# 🛠️ 5. SERVICE SERIALIZERS
# ==========================================

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializes Service listings with readable category names.
    """
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )

    provider_name = serializers.CharField(source='provider.profile.user.username', read_only=True)

    class Meta:
        model = Service

        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'service_city', 
            'status', 
            'category', 
            'provider', 
            'provider_name', 
            'created_at', 
            'updated_at'
        ]

class CreateServiceSerializer(serializers.ModelSerializer):
    """
    Serializes Service creation with Category ID.
    ✅ CHANGED: Now accepts Category ID instead of string name.
    """
    # ✅ ONLY CHANGE: Category uses ID (Primary Key) instead of string name
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(category_type='SERVICE'),
        required=True,
        allow_null=False,
        error_messages={
            'does_not_exist': 'Invalid category ID. Please select a valid category.',
            'incorrect_type': 'Category ID must be an integer.',
            'null': 'Category is required.',
            'required': 'Category is required.'
        }
    )
    
    image = serializers.ImageField(required=False, write_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['provider', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        uploaded_image = validated_data.pop('image', None)
        service = super().create(validated_data)
        
        if uploaded_image:
            from .models import ServiceImage
            try:
                ServiceImage.objects.create(
                    service=service,
                    image=uploaded_image,
                    is_feature=True
                )
            except Exception as e:
                logger.error(f"Failed to attach image to Service ID {service.id}: {e}")
        
        return service


# ==========================================
# 👤 6. USER & INQUIRY SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ServiceInquirySerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    service_inquired = serializers.CharField(source='service.name', read_only=True)
    message_preview = serializers.SerializerMethodField()
    date_received = serializers.DateTimeField(source='created_at', format="%b %d, %Y %I:%M %p", read_only=True)

    class Meta:
        model = ServiceInquiry
        fields = [
            'id', 'client', 'client_name', 'client_username', 
            'service', 'service_inquired', 'message', 
            'message_preview', 'status', 'date_received',
        ]
        read_only_fields = ['client', 'status', 'created_at']

    def get_message_preview(self, obj):
        if len(obj.message) > 40:
            return obj.message[:40] + "..."
        return obj.message


class UserProfileStatusSerializer(serializers.ModelSerializer):
    approval_status = serializers.SerializerMethodField()
    has_provider_profile = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'approval_status', 'has_provider_profile']

    def get_has_provider_profile(self, obj):
        return hasattr(obj, 'service_profile')

    def get_approval_status(self, obj):
        if hasattr(obj, 'service_profile'):
            return obj.service_profile.approval_status
        return None