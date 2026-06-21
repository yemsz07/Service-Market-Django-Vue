from rest_framework import serializers
from .models import Product, Category, Service, ProductImage

# 1. Serializer para sa Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type']

# 2. Serializer para sa Images (para makuha ang actual image file path)
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_feature', 'uploaded_at']

# 3. Serializer para sa Product
class ProductSerializer(serializers.ModelSerializer):
    # I-link ang category (one-to-one or foreign key relation)
    category = CategorySerializer(read_only=True)
    
    # I-link ang images (dito papasok yung related_name='images' mula sa model)
    # Ang 'many=True' ay dahil ang isang product ay pwedeng may maraming images
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        # Gamitin ang '__all__' o ilista ang fields kabilang ang 'category' at 'images'
        fields = ['id', 'name', 'description', 'price', 'city', 'status',
                  'category', 'images']

# 4. Serializer para sa Service
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'