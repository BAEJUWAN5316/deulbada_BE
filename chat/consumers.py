import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.info(f"🔥 WebSocket received: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get('message')
            logger.info(f"✏️ Parsed message: {message_content}")

            user = self.scope['user']
            if not user.is_authenticated:
                logger.warning(f"Unauthenticated user tried to send message in room {self.room_name}")
                return

            try:
                chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_name)
            except ChatRoom.DoesNotExist:
                logger.error(f"ChatRoom with ID {self.room_name} does not exist.")
                return

            await sync_to_async(Message.objects.create)(
                room=chat_room,
                sender=user,
                content=message_content
            )
            logger.info(f"💾 Message saved to DB for room {self.room_name}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # Use underscore instead of dot
                    'message': message_content,
                    'sender': user.username
                }
            )
            logger.info(f"✅ Message broadcast initiated for group {self.room_group_name}")

        except Exception as e:
            logger.error(f"❌ Error in receive method: {e}")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
        logger.info(f"📤 Sent message to WebSocket client in room {self.room_name}")
