# chatapp/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import DirectMessage

User = get_user_model()

class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.target_user_id = self.scope['url_route']['kwargs']['target_user_id']

        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        sender_id = str(self.user.id)
        user_ids = sorted([sender_id, str(self.target_user_id)])

        self.room_name = f"dm_{user_ids[0]}_{user_ids[1]}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        service_name = data.get('service_name', None)

        if not message_text:
            return

        # 🔧 CHANGED: wrapped sa try/except para hindi tumigil nang tahimik ang consumer
        # kung invalid ang target_user_id (hal. nag-DoesNotExist ang recipient lookup)
        try:
            saved_msg, notification = await self.save_message(
                sender=self.user,
                recipient_id=self.target_user_id,
                message=message_text,
                service_name=service_name
            )
        except Exception:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to send message.'
            }))
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': str(saved_msg.id),
                'message': saved_msg.message,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'timestamp': saved_msg.timestamp.strftime('%H:%M'),
            }
        )

        if notification:
            await self.broadcast_notification(
                recipient_id=self.target_user_id,
                notification_id=notification.id,
                sender=self.user,
                message=message_text,
                service_name=service_name
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, recipient_id, message, service_name=None):
        try:
            # 🔧 CHANGED: TINANGGAL ang pag-print ng buong mongo_settings dict —
            # kasama doon ang MONGO_URI na may username/password. Ito ang pinaka-
            # importanteng fix dito — credential leak sa logs kada may padalang message.
            recipient = User.objects.using('default').get(id=recipient_id)
            saved_msg = DirectMessage.objects.using('mongodb').create(
                sender=sender,
                recipient=recipient,
                message=message
            )

            notification = self.create_notification_sync(
                recipient=recipient,
                sender=sender,
                message=message,
                service_name=service_name
            )

            return saved_msg, notification
        except Exception as e:
            # 🔧 CHANGED: log na lang ang error type, hindi buong traceback+settings sa prod
            print(f"[MongoDB] Error saving message: {e}")
            raise

    def create_notification_sync(self, recipient, sender, message, service_name=None):
        try:
            from djbcknd.models import Notification

            if service_name:
                title = f'New message about "{service_name}"'
            else:
                title = f'New message from {sender.username}'

            notification = Notification.objects.using('default').create(
                recipient=recipient,
                sender=sender,
                notification_type='MESSAGE',
                title=title,
                service_name=service_name,
                message=message[:100] + '...' if len(message) > 100 else message,
                is_read=False
            )
            return notification
        except Exception as e:
            print(f"[NOTIFICATION] Error creating notification: {e}")
            return None

    async def broadcast_notification(self, recipient_id, notification_id, sender, message, service_name=None):
        try:
            recipient_room = f"user_notifications_{recipient_id}"

            await self.channel_layer.group_send(
                recipient_room,
                {
                    'type': 'notification_event',
                    'data': {
                        'id': notification_id,
                        'notification_type': 'MESSAGE',
                        'title': f'New message about "{service_name}"' if service_name else f'New message from {sender.username}',
                        'message': message[:100] + '...' if len(message) > 100 else message,
                        'sender_name': sender.username,
                        'sender_id': sender.id,
                        'is_read': False,
                        'created_at': None,
                        'service_name': service_name
                    }
                }
            )
        except Exception as e:
            print(f"[NOTIFICATION WS] Error broadcasting notification: {e}")