from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from chatapp.models import DirectMessage  # O paliitan ayon sa path ng Message model mo

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    current_user = request.user

    # Kukunin ang mga huling mensahe sa pagitan ni request.user at ibang users
    messages = DirectMessage.objects.filter(
        Q(sender=current_user) | Q(recipient=current_user)
    ).order_by('-timestamp')

    conversations_dict = {}
    
    for msg in messages:
        other_user = msg.recipient if msg.sender == current_user else msg.sender
        
        if other_user.id not in conversations_dict:
            conversations_dict[other_user.id] = {
                'id': f"conv_{other_user.id}",
                'targetUserId': other_user.id,
                'name': other_user.username,
                'lastMessage': msg.message,
                'time': msg.timestamp.strftime('%H:%M'),
                'online': True,
                'unread': False
            }

    return Response(list(conversations_dict.values()))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, user_id):
    current_user = request.user

    # Kukunin ang chat history sa pagitan ng dalawang user
    messages = DirectMessage.objects.filter(
        (Q(sender=current_user) & Q(recipient_id=user_id)) |
        (Q(sender_id=user_id) & Q(recipient=current_user))
    ).order_by('timestamp')

    data = [
        {
            'id': str(msg.id),
            'text': msg.message,
            'sender': 'me' if msg.sender_id == current_user.id else 'them',
            'time': msg.timestamp.strftime('%H:%M')
        }
        for msg in messages
    ]

    return Response(data)