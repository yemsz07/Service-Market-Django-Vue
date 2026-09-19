from rest_framework import serializers

from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'sender',
            'sender_name',
            'service',
            'service_name',
            'inquiry',
            'is_read',
            'created_at'
        ]
        read_only_fields = ['created_at']