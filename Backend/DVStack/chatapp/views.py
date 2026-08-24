# chatapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import DirectMessage

class MessageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, target_user_id):
        # Native Django ORM Query across MongoDB
        messages = DirectMessage.objects.filter(
            (Q(sender=request.user) & Q(recipient_id=target_user_id)) |
            (Q(sender_id=target_user_id) & Q(recipient=request.user))
        ).order_by('timestamp')

        history = [
            {
                'id': msg.id,
                'message': msg.message,
                'sender_id': msg.sender_id,
                'is_me': msg.sender_id == request.user.id,
                'timestamp': msg.timestamp.strftime('%H:%M')
            }
            for msg in messages
        ]

        return Response(history)