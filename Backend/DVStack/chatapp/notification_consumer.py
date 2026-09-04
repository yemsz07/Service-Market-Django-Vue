# chatapp/notification_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each user connects to their own notification room: user_notifications_{user_id}
    """
    async def connect(self):
        self.user = self.scope.get('user')

        if not self.user or self.user.is_anonymous:
            print(f"[NOTIFICATION WS] Anonymous user attempting to connect")
            await self.close(code=4001)
            return

        # Create room based on current user's ID
        self.room_group_name = f"user_notifications_{self.user.id}"

        print(f"[NOTIFICATION WS] User {self.user.username} (ID: {self.user.id}) connecting to room: {self.room_group_name}")

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
            print(f"[NOTIFICATION WS] User {self.user.username} disconnected from room: {self.room_group_name}")

    async def receive(self, text_data):
        # This consumer is primarily for receiving notifications, not sending
        # But we can handle any client-initiated messages if needed
        pass

    async def notification_event(self, event):
        """
        Handle incoming notification events from the channel layer.
        This is called when a notification is broadcast to this user's room.
        """
        # Send the notification data to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event.get('data')
        }))
