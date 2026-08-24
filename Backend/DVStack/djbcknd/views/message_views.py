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
        Q(sender_id=current_user.id) | Q(recipient_id=current_user.id)
    ).order_by('-timestamp')

    conversations_dict = {}
    user_ids = set()
    
    # Collect all unique user IDs from messages
    for msg in messages:
        if msg.sender_id != current_user.id:
            user_ids.add(msg.sender_id)
        if msg.recipient_id != current_user.id:
            user_ids.add(msg.recipient_id)
    
    # Fetch all users from PostgreSQL in a single query
    users = {user.id: user for user in User.objects.filter(id__in=user_ids)}
    
    for msg in messages:
        # Use ID fields directly instead of accessing related objects
        other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        other_user = users.get(other_user_id)
        
        if other_user and other_user_id not in conversations_dict:
            conversations_dict[other_user_id] = {
                'id': f"conv_{other_user_id}",
                'targetUserId': other_user_id,
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