from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from asgiref.sync import async_to_sync, sync_to_async
from chatapp.models import DirectMessage
from chatapp.presence import ONLINE_WINDOW
from djbcknd.models import Product, Service, Profile

User = get_user_model()


# ==========================================
# NON-BLOCKING DATABASE QUERY HELPERS
# ==========================================

@sync_to_async
def fetch_conversations_data(authenticated_user_id):
    messages = list(
        DirectMessage.objects.using('mongodb').filter(
            Q(sender_id=authenticated_user_id) | Q(recipient_id=authenticated_user_id)
        ).order_by('-timestamp')[:100]
    )

    if not messages:
        return []

    user_ids, product_ids, service_ids = set(), set(), set()

    for msg in messages:
        other_id = msg.recipient_id if msg.sender_id == authenticated_user_id else msg.sender_id
        user_ids.add(other_id)

        p_id = getattr(msg, 'product_id', None)
        s_id = getattr(msg, 'service_id', None)
        if p_id:
            product_ids.add(p_id)
        if s_id:
            service_ids.add(s_id)

    # ---- BATCH QUERIES (isang tawag bawat table) ----
    users = {u.id: u for u in User.objects.using('default').filter(id__in=user_ids)}

    products = (
        {p.id: p for p in Product.objects.using('default').filter(id__in=product_ids)}
        if product_ids else {}
    )
    services = (
        {s.id: s for s in Service.objects.using('default').filter(id__in=service_ids)}
        if service_ids else {}
    )

    # 🆕 PRESENCE BATCH QUERY — isang query lang para sa lahat
    presence_map = {
        p.user_id: p.last_seen_at
        for p in Profile.objects.using('default').filter(user_id__in=user_ids)
    }
    now = timezone.now()

    # ---- FORMAT PAYLOAD ----
    conversations_dict = {}
    for msg in messages:
        other_user_id = msg.recipient_id if msg.sender_id == authenticated_user_id else msg.sender_id
        other_user = users.get(other_user_id)

        if not other_user or other_user_id in conversations_dict:
            continue

        # 🆕 Compute online from batch data — zero extra query
        last_seen = presence_map.get(other_user_id)
        is_online = last_seen is not None and (now - last_seen) < ONLINE_WINDOW

        p_id = getattr(msg, 'product_id', None)
        s_id = getattr(msg, 'service_id', None)

        item_data = None
        if p_id and p_id in products:
            prod = products[p_id]
            item_data = {
                'id': str(prod.id),
                'title': getattr(prod, 'name', getattr(prod, 'title', '')),
                'price': float(prod.price),
                'image': prod.image.url if getattr(prod, 'image', None) else '',
                'type': 'buy_and_sell',
            }
        elif s_id and s_id in services:
            serv = services[s_id]
            item_data = {
                'id': str(serv.id),
                'title': getattr(serv, 'name', getattr(serv, 'title', '')),
                'price': float(serv.price),
                'image': serv.image.url if getattr(serv, 'image', None) else '',
                'type': 'services',
            }

        conversations_dict[other_user_id] = {
            'id': f"conv_{other_user_id}",
            'targetUserId': other_user_id,
            'seller_id': other_user_id,
            'name': other_user.username,
            'lastMessage': msg.message,
            'time': msg.timestamp.strftime('%H:%M'),
            'online': is_online,   # 🆕 TOTOONG PRESENCE
            'unread': False,
            'item': item_data,
        }

    return list(conversations_dict.values())


@sync_to_async
def create_initial_item_chat(sender_id, recipient_id, product_id=None, service_id=None):
    msg = DirectMessage.objects.using('mongodb').create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message="Hi! I am interested in this listing.",
        product_id=product_id,
        service_id=service_id,
    )
    return str(msg.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_item_chat(request):
    authenticated_user_id = request.user.id
    recipient_id = request.data.get('seller_id')
    product_id = request.data.get('product_id')
    service_id = request.data.get('service_id')

    # ---- VALIDATION ----
    if not recipient_id:
        return Response(
            {"error": "seller_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if recipient_id == authenticated_user_id:
        return Response(
            {"error": "Cannot start a chat with yourself"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not User.objects.using('default').filter(id=recipient_id).exists():
        return Response(
            {"error": "Recipient user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # ---- ERROR HANDLING ----
    try:
        message_id = async_to_sync(create_initial_item_chat)(
            sender_id=authenticated_user_id,
            recipient_id=recipient_id,
            product_id=product_id,
            service_id=service_id,
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to start chat: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"message": "Chat initiated successfully", "message_id": message_id},
        status=status.HTTP_200_OK,
    )


@sync_to_async
def fetch_chat_history_data(authenticated_user_id, target_user_id):
    messages = list(
        DirectMessage.objects.using('mongodb').filter(
            (Q(sender_id=authenticated_user_id) & Q(recipient_id=target_user_id))
            | (Q(sender_id=target_user_id) & Q(recipient_id=authenticated_user_id))
        ).order_by('timestamp')
    )

    return [
        {
            'id': str(msg.id),
            'text': msg.message,
            'sender': 'me' if msg.sender_id == authenticated_user_id else 'them',
            'time': msg.timestamp.strftime('%H:%M'),
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
    data = async_to_sync(fetch_conversations_data)(authenticated_user_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, user_id):
    authenticated_user_id = request.user.id
    data = async_to_sync(fetch_chat_history_data)(
        authenticated_user_id, target_user_id=user_id
    )
    return Response(data)