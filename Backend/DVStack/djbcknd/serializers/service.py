import logging

from rest_framework import serializers

from ..models import Category, Service

logger = logging.getLogger(__name__)


# ==========================================
# 🛠️ SERVICE SERIALIZERS
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
    provider_user_id = serializers.IntegerField(source='provider.profile.user.id', read_only=True)
    provider_avatar = serializers.CharField(source='provider.provider_avatar', read_only=True)
    image = serializers.SerializerMethodField()

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
            'provider_user_id',
            'provider_avatar',
            'image',
            'created_at',
            'updated_at'
        ]

    def get_image(self, obj):
        # Kung ang Service model ay may related_name na 'images' para sa ServiceImage
        first_img = getattr(obj, 'images', None)
        if first_img:
            img_obj = first_img.first()
            if img_obj and img_obj.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(img_obj.image.url)
                return img_obj.image.url
        return None


class CreateServiceSerializer(serializers.ModelSerializer):
    """
    Serializes Service creation with Category ID.
    ✅ CHANGED: Now accepts Category ID instead of string name.
    """
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
            from ..models import ServiceImage
            try:
                ServiceImage.objects.create(
                    service=service,
                    image=uploaded_image,
                    is_feature=True
                )
            except Exception as e:
                logger.error(f"Failed to attach image to Service ID {service.id}: {e}")

        return service