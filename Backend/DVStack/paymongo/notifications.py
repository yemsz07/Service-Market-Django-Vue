"""
Helper for broadcasting "payment released" notification to
seller/provider, using the SAME channel layer pattern used
by your chatapp/consumers.py (group_name = user_notifications_{id},
event type = notification_event).

This is deliberately NOT an async function — because it's called from
SYNC Django Ninja endpoints (api.py) and management command
(auto_release_payments.py), it needs the async_to_sync wrapper.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from djbcknd.models import Notification

from .services.dispute import get_provider_user


def notify_payment_released(txn):
    """
    Sends notification to the seller/provider of a
    transaction after payment is released (manual or auto).

    Uses the SAME mechanism (Notification DB record +
    channel_layer broadcast) used in your chat notifications,
    for consistent behavior and visibility in notification list
    (not just as a popup).
    """
    recipient = get_provider_user(txn)
    if recipient is None:
        # No identifiable seller/provider (shouldn't happen in
        # normal operation, but don't crash the release
        # flow if it does).
        return

    item_name = None
    if txn.product_id:
        item_name = txn.product.name
    elif txn.service_id:
        item_name = txn.service.name

    message_text = f"The payment of ₱{txn.amount:,.2f} for '{item_name}' has been released to your account."

    # 1. Save to DB, so it also appears in notification list/history
    #    (not just as a one-time popup).
    notification = Notification.objects.using('default').create(
        recipient=recipient,
        sender=txn.user,  # buyer as "sender" (context: they paid)
        notification_type='PAYMENT_RELEASED',
        title="Payment Released!",
        service_name=item_name,
        message=message_text,
        is_read=False,
    )

    # 2. Broadcast real-time via WebSocket, SAME group naming and
    #    event type used in your chatapp/consumers.py.
    channel_layer = get_channel_layer()
    recipient_room = f"user_notifications_{recipient.id}"

    async_to_sync(channel_layer.group_send)(
        recipient_room,
        {
            'type': 'notification_event',
            'data': {
                'id': notification.id,
                'notification_type': 'PAYMENT_RELEASED',
                'title': "Payment Released!",
                'message': message_text,
                'sender_name': txn.user.username,
                'sender_id': txn.user.id,
                'is_read': False,
                'created_at': notification.created_at.isoformat() if hasattr(notification, 'created_at') else None,
                'service_name': item_name,
                # Additional field, specific to payment context — for
                # frontend to trigger POPUP (not
                # just regular notification entry in list).
                'reference_number': txn.reference_number,
                'amount': float(txn.amount),
            }
        }
    )

