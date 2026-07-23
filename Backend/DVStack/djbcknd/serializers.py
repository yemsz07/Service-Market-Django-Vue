"""
Serializers configuration for djbcknd app.
Translates Django database models into JSON format (and vice versa) for API requests.
"""

# ==========================================
# 📦 1. IMPORTS (Preparing our tools)
# ==========================================

import logging  # 📜 Logger: Used to record backend errors/warnings.

from django.contrib.auth.models import User  # 👤 Default Django User model.
from django.core.validators import FileExtensionValidator  # 🛡️ File Guard: Restricts allowed image file formats.
from rest_framework import serializers  # 🗣️ DRF Serializers: Converts Python objects <-> JSON data.

from .models import Category, Product, ProductImage, Service  # 🧸 Database Models to serialize.

logger = logging.getLogger(__name__)


# ==========================================
# 🏷️ 2. CATEGORY SERIALIZER
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes Category data (e.g., Electronics, Services) into simple JSON.
    """
    class Meta:
        model = Category  # 🎯 Link to Category model.
        fields = ['id', 'name', 'category_type']  # 📋 Fields to include in the output.


# ==========================================
# 🖼️ 3. PRODUCT IMAGE SERIALIZER
# ==========================================

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Handles individual product images and formats their full URL links.
    """
    image = serializers.SerializerMethodField()  # 🛠️ Custom dynamic field to build full Image URLs.

    class Meta:
        model = ProductImage  # 🎯 Link to ProductImage model.
        fields = ['id', 'image', 'is_feature', 'uploaded_at']  # 📋 Fields to include in JSON output.

    def get_image(self, obj):
        """
        Dynamically attaches the full domain (e.g., http://localhost:8000/media/...) to the image path.
        """
        if obj.image:
            request = self.context.get('request')  # 📷 Get active HTTP request details from context.
            if request:
                return request.build_absolute_uri(obj.image.url)  # 🔗 Returns full absolute URL with domain.
            return obj.image.url  # 🔗 Fallback to relative URL path if request context is missing.
        return None  # 🚫 Return None if no image exists.


# ==========================================
# 📦 4. PRODUCT SERIALIZER
# ==========================================

class ProductSerializer(serializers.ModelSerializer):
    """
    Main Product Serializer: Handles product details, image upload validations, and primary image resolution.
    """
    category = CategorySerializer(read_only=True)  # 🏷️ Nested full Category details (Read-only).
    images = ProductImageSerializer(many=True, read_only=True)  # 🖼️ List of all attached images.
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # 🏙️ Optional location field.
    
    # 🛡️ File extension validation for uploaded images during creation:
    image = serializers.ImageField(
        required=False, 
        write_only=True,  # 📝 Used only when sending data to backend (hidden in GET responses).
        allow_empty_file=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]  # 🔒 Only allowed formats!
    )
    seller = serializers.PrimaryKeyRelatedField(read_only=True)  # 👤 Links to seller ID (Read-only).
    primary_image = serializers.SerializerMethodField()  # ⭐️ Custom field for display image thumbnail.

    class Meta:
        model = Product  # 🎯 Link to Product model.
        fields = [
            'id', 'name', 'description', 'price', 'city', 'status',
            'category', 'images', 'seller', 'image', 'primary_image'
        ]  # 📋 All fields included in JSON.

    def get_primary_image(self, obj):
        """
        Extracts the first attached image and returns its absolute URL as the primary cover photo.
        """
        first_img = obj.images.first()  # 🔍 Look for the first image in the product's gallery.
        if first_img and first_img.image:
            request = self.context.get('request')  # 📷 Get request context.
            if request:
                return request.build_absolute_uri(first_img.image.url)  # 🔗 Return full absolute URL.
            return first_img.image.url  # 🔗 Fallback to relative URL.
        return None  # 🚫 Return None if no images are attached.

    def create(self, validated_data):
        """
        Overrides product creation logic to safely extract uploaded image file and create ProductImage entry.
        """
        uploaded_image = validated_data.pop('image', None)  # ✂️ Remove 'image' from payload so Product model can save cleanly.
        product = super().create(validated_data)  # 💾 Create and save base Product instance.
        
        # 🛡️ Safe error handling during image creation:
        if uploaded_image:
            try:
                # 🖼️ Automatically attach image to ProductImage model as featured image:
                ProductImage.objects.create(product=product, image=uploaded_image, is_feature=True)
            except Exception as e:
                logger.error(f"Failed to create ProductImage for Product ID {product.id}: {e}")  # 📜 Log error without crashing app!
            
        return product  # 🎁 Return newly created product instance.


# ==========================================
# 🛠️ 5. SERVICE SERIALIZER
# ==========================================

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializes Service listings with readable category names.
    """
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'  # 🏷️ Shows category name string instead of just raw ID number (e.g. "Plumbing" vs "1").
    )

    class Meta:
        model = Service  # 🎯 Link to Service model.
        fields = '__all__'  # 📋 Includes every column defined in Service model.


# ==========================================
# 👤 6. USER SERIALIZER
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    """
    Handles user account creation and password hashing logic.
    """
    class Meta:
        model = User  # 🎯 Link to Django User model.
        fields = ['username', 'email', 'password']  # 📋 Registration inputs required.
        extra_kwargs = {'password': {'write_only': True}}  # 🔒 Keeps password hidden in API responses for security.

    def create(self, validated_data):
        """
        Creates new user account securely using Django's built-in password hashing method.
        """
        user = User.objects.create_user(**validated_data)  # 🔐 Encrypts password automatically before saving to DB.
        return user  # 🎁 Return new user object.