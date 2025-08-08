import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom # Message, ChatRoom 모델 임포트
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async # 비동기 코드에서 동기 ORM 호출을 위해 필요

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        # 현재 연결된 사용자 (scope['user']에 인증된 사용자 객체가 있다고 가정)
        user = self.scope['user']
        if not user.is_authenticated:
            # 인증되지 않은 사용자라면 메시지 저장 불가 또는 에러 처리
            print("인증되지 않은 사용자입니다. 메시지를 저장할 수 없습니다.")
            return

        # room_name을 기반으로 ChatRoom 찾기
        # room_name이 ChatRoom의 ID라고 가정합니다. (예: /ws/chat/3/ 에서 3)
        try:
            chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_name)
        except ChatRoom.DoesNotExist:
            print(f"ChatRoom with ID {self.room_name} does not exist.")
            return

        # 데이터베이스에 메시지 저장
        try:
            await sync_to_async(Message.objects.create)(
                room=chat_room,
                sender=user,
                content=message_content
            )
        except Exception as e:
            print(f"메시지 저장 중 오류 발생: {e}")
            # 에러 처리 로직 추가

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message_content,
                'sender': user.username # 프론트엔드로 보낼 발신자 이름
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender'] # 발신자 정보 받기

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
