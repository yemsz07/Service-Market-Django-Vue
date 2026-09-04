from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync, sync_to_async
from chatapp.models import DirectMessage

User = get_user_model()

# ==========================================
# NON-BLOCKING DATABASE QUERY HELPERS
# ==========================================

@sync_to_async
def fetch_conversations_data(authenticated_user_id):
    # 1. Direct non-blocking fetch from MongoDB
    messages = list(
        DirectMessage.objects.using('mongodb').filter(
            Q(sender_id=authenticated_user_id) | Q(recipient_id=authenticated_user_id)
        ).order_by('-timestamp')[:100]
    )

    if not messages:
        return []

    # 2. Extract unique chat partners
    user_ids = {
        msg.sender_id if msg.sender_id != authenticated_user_id else msg.recipient_id 
        for msg in messages
    }

    # 3. Explicit query to PostgreSQL for User Auth profiles
    users = {user.id: user for user in User.objects.using('default').filter(id__in=user_ids)}

    # 4. Format payload
    conversations_dict = {}
    for msg in messages:
        other_user_id = msg.recipient_id if msg.sender_id == authenticated_user_id else msg.sender_id
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

    return list(conversations_dict.values())


@sync_to_async
def fetch_chat_history_data(authenticated_user_id, target_user_id):
    # Strict boundary check: User can only read messages involving themselves
    messages = list(
        DirectMessage.objects.using('mongodb').filter(
            (Q(sender_id=authenticated_user_id) & Q(recipient_id=target_user_id)) |
            (Q(sender_id=target_user_id) & Q(recipient_id=authenticated_user_id))
        ).order_by('timestamp')
    )

    return [
        {
            'id': str(msg.id),
            'text': msg.message,
            'sender': 'me' if msg.sender_id == authenticated_user_id else 'them',
            'time': msg.timestamp.strftime('%H:%M')
        }
        for msg in messages
    ]


# ==========================================
# SAFE SYNC DRF VIEWS (ASGI-COMPATIBLE)
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    authenticated_user_id = request.user.id
    # Executes async MongoDB query synchronously without blocking the ASGI event loop
    data = async_to_sync(fetch_conversations_data)(authenticated_user_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, user_id):
    authenticated_user_id = request.user.id
    data = async_to_sync(fetch_chat_history_data)(authenticated_user_id, target_user_id=user_id)
    return Response(data)