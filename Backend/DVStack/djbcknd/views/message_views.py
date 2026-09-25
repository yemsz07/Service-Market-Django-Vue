from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync, sync_to_async
from chatapp.models import DirectMessage
from djbcknd.models import Product, Service

User = get_user_model()

# ==========================================
# NON-BLOCKING DATABASE QUERY HELPERS
# ==========================================

from djbcknd.models import Product, Service # I-import ang totoong models mo sa PostgreSQL

@sync_to_async
def fetch_conversations_data(authenticated_user_id):
    # 1. Fetch recent messages from MongoDB
    messages = list(
        DirectMessage.objects.using('mongodb').filter(
            Q(sender_id=authenticated_user_id) | Q(recipient_id=authenticated_user_id)
        ).order_by('-timestamp')[:100]
    )

    if not messages:
        return []

    # 2. Extract unique User IDs, Product IDs, at Service IDs mula sa MongoDB messages
    user_ids = set()
    product_ids = set()
    service_ids = set()

    for msg in messages:
        # Collect partner user IDs
        other_id = msg.recipient_id if msg.sender_id == authenticated_user_id else msg.sender_id
        user_ids.add(other_id)

        # Collect PostgreSQL Item IDs (kung mayroon sa message object)
        p_id = getattr(msg, 'product_id', None)
        s_id = getattr(msg, 'service_id', None)
        if p_id:
            product_ids.add(p_id)
        if s_id:
            service_ids.add(s_id)

    # 3. BATCH QUERY sa PostgreSQL (Gamit ang default database)
    users = {u.id: u for u in User.objects.using('default').filter(id__in=user_ids)}
    
    # Kukuha ng Products at Services diretso sa PostgreSQL tables
    products = {p.id: p for p in Product.objects.using('default').filter(id__in=product_ids)} if product_ids else {}
    services = {s.id: s for s in Service.objects.using('default').filter(id__in=service_ids)} if service_ids else {}

    # 4. Format payload para sa Vue Frontend Header
    conversations_dict = {}
    for msg in messages:
        other_user_id = msg.recipient_id if msg.sender_id == authenticated_user_id else msg.sender_id
        other_user = users.get(other_user_id)

        if other_user and other_user_id not in conversations_dict:
            # Kunin ang PostgreSQL Item Instance
            p_id = getattr(msg, 'product_id', None)
            s_id = getattr(msg, 'service_id', None)
            
            item_data = None
            if p_id and p_id in products:
                prod = products[p_id]
                item_data = {
                    'id': str(prod.id),
                    'title': getattr(prod, 'name', getattr(prod, 'title', '')), # I-adjust sa field name ng Product model mo
                    'price': float(prod.price),
                    'image': prod.image.url if getattr(prod, 'image', None) else '',
                    'type': 'buy_and_sell'
                }
            elif s_id and s_id in services:
                serv = services[s_id]
                item_data = {
                    'id': str(serv.id),
                    'title': getattr(serv, 'name', getattr(serv, 'title', '')), # I-adjust sa field name ng Service model mo
                    'price': float(serv.price),
                    'image': serv.image.url if getattr(serv, 'image', None) else '',
                    'type': 'services'
                }

            conversations_dict[other_user_id] = {
                'id': f"conv_{other_user_id}",
                'targetUserId': other_user_id,
                'seller_id': other_user_id,
                'name': other_user.username,
                'lastMessage': msg.message,
                'time': msg.timestamp.strftime('%H:%M'),
                'online': True,
                'unread': False,
                'item': item_data  # <-- Karga na rito ang totoong PostgreSQL item data!
            }

    return list(conversations_dict.values())



@sync_to_async
def create_initial_item_chat(sender_id, recipient_id, product_id=None, service_id=None):
    # MongoDB write: Nag-iwan lang tayo ng Reference ID papunta sa PostgreSQL
    msg = DirectMessage.objects.using('mongodb').create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message="Hi! I am interested in this listing.",
        product_id=product_id,
        service_id=service_id
    )
    return str(msg.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_item_chat(request):
    authenticated_user_id = request.user.id
    recipient_id = request.data.get('seller_id')
    product_id = request.data.get('product_id')
    service_id = request.data.get('service_id')

    async_to_sync(create_initial_item_chat)(
        sender_id=authenticated_user_id,
        recipient_id=recipient_id,
        product_id=product_id,
        service_id=service_id
    )

    return Response({"message": "Chat initiated successfully"}, status=200)



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