import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # JWT 토큰 인증
        token = await self.get_token_from_query()
        if token:
            user = await self.authenticate_token(token)
            if user:
                self.scope['user'] = user
                logger.info(f"✅ User {user.username} authenticated via JWT token")
            else:
                logger.warning("❌ Invalid JWT token")
                await self.close(code=4001)
                return
        else:
            logger.warning("❌ No JWT token provided")
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
    async def get_token_from_query(self):
        """쿼리 파라미터에서 JWT 토큰 추출"""
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        return token
    
    async def authenticate_token(self, token):
        """JWT 토큰 인증 및 사용자 반환"""
        try:
            # JWT 토큰 검증
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # 사용자 객체 가져오기
            user = await sync_to_async(User.objects.get)(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.error(f"❌ Token authentication failed: {e}")
            return None

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
            image_url = text_data_json.get('image_url')  # Get image_url
            logger.info(f"✏️ Parsed message: {message_content}, image_url: {image_url}")

            user = self.scope['user']

            try:
                chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_name)
            except ChatRoom.DoesNotExist:
                logger.error(f"ChatRoom with ID {self.room_name} does not exist.")
                return

            # Create message with content and image_url
            await sync_to_async(Message.objects.create)(
                room=chat_room,
                sender=user,
                content=message_content,
                image_url=image_url
            )
            logger.info(f"💾 Message saved to DB for room {self.room_name}")

            # Broadcast with image_url
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': user.username,
                    'image_url': image_url
                }
            )
            logger.info(f"✅ Message broadcast initiated for group {self.room_group_name}")

        except Exception as e:
            logger.error(f"❌ Error in receive method: {e}")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        image_url = event.get('image_url') # Get image_url from event

        # Send all fields to client
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'image_url': image_url
        }))
        logger.info(f"📤 Sent message to WebSocket client in room {self.room_name}")