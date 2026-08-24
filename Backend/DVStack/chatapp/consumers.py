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

        # 🛡️ Auth Check - Allow connection but log if anonymous
        if not self.user or self.user.is_anonymous:
            print(f"[WS] Anonymous user attempting to connect to chat with user {self.target_user_id}")
            await self.close(code=4001)
            return

        print(f"[WS] User {self.user.username} connecting to chat with user {self.target_user_id}")

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

        if not message_text:
            return

        # 🟢 1. Native Django ORM Save (Awtomatikong nagsusulat sa MongoDB)
        saved_msg = await self.save_message(
            sender=self.user,
            recipient_id=self.target_user_id,
            message=message_text
        )

        # 🟢 2. Broadcast sa Channels Group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': str(saved_msg.id),  # Convert ObjectId to string
                'message': saved_msg.message,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'timestamp': saved_msg.timestamp.strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # 💾 Standard Django ORM Wrapper with explicit MongoDB routing
    @database_sync_to_async
    def save_message(self, sender, recipient_id, message):
        try:
            from django.conf import settings
            
            # Log MongoDB connection details
            mongo_settings = settings.DATABASES.get('mongodb', {})
            print(f"[MongoDB] Connection settings: {mongo_settings}")
            print(f"[MongoDB] Database name: {mongo_settings.get('NAME')}")
            print(f"[MongoDB] Host: {mongo_settings.get('HOST')}")
            
            recipient = User.objects.using('default').get(id=recipient_id)
            saved_msg = DirectMessage.objects.using('mongodb').create(
                sender=sender,
                recipient=recipient,
                message=message
            )
            print(f"[MongoDB] Message saved with ID: {saved_msg.id}")
            print(f"[MongoDB] Collection: chatapp_directmessage (app_label: {DirectMessage._meta.app_label}, model: {DirectMessage._meta.model_name})")
            return saved_msg
        except Exception as e:
            print(f"[MongoDB] Error saving message: {e}")
            import traceback
            traceback.print_exc()
            raise