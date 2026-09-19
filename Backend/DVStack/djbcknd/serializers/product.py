import logging

from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from ..models import Product, ProductImage
from .category import CategorySerializer

logger = logging.getLogger(__name__)


# ==========================================
# 🖼️ PRODUCT IMAGE SERIALIZER
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
# 📦 PRODUCT SERIALIZER
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

    seller_user_id = serializers.ReadOnlyField(source='seller.user.id', default=None)
    seller_username = serializers.ReadOnlyField(source='seller.user.username', default=None)
    seller_avatar = serializers.SerializerMethodField()

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'city', 'status',
            'category', 'images', 'seller', 'image', 'primary_image',
            'seller_user_id', 'seller_username', 'seller_avatar',
        ]

    def get_seller_avatar(self, obj):
        """
        Ligtas na kinukuha ang avatar URL ng seller gamit ang null-checks.
        """
        if hasattr(obj, 'seller') and obj.seller and getattr(obj.seller, 'avatar', None):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.seller.avatar.url)
            return obj.seller.avatar.url
        return None

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