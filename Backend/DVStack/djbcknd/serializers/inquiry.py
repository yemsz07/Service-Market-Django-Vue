from rest_framework import serializers

from ..models import ServiceInquiry


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