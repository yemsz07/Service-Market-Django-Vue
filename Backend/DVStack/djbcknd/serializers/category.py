from rest_framework import serializers

from ..models import Category


# ==========================================
# 🏷️ CATEGORY SERIALIZER
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes Category data into simple JSON.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'slug']