from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password  # 🔧 CHANGED: added
from rest_framework import serializers
from rest_framework.validators import UniqueValidator  # 🔧 CHANGED: added

from ..models import Profile


# ==========================================
# 👤 USER SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    # 🔧 CHANGED: explicit email field — required + unique, para walang duplicate accounts
    # gamit ang parehong email (importante ito kapag gagamitin mo email para sa password reset)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # 🔧 CHANGED: idinagdag — dati walang password strength check, kahit "1" na password
        # ay papasa. Gagamitin nito ang AUTH_PASSWORD_VALIDATORS mo sa settings.py
        # (min length, common password check, similarity sa username, atbp.)
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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