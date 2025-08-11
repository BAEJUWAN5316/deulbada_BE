# chat/serializers.py
from rest_framework import serializers
from django.conf import settings
from .models import ChatRoom, Message
from users.serializers import UserSerializer #   ֱ  SimpleUserSerializer 
from django.contrib.auth import get_user_model
User = get_user_model() 

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_username', 'content', 'image_url', 'is_read', 'created_at']
        read_only_fields = ['sender', 'room', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    # 유저 정보는 중첩 직렬화 대신 PK만 노출
    user1 = serializers.PrimaryKeyRelatedField(read_only=True)
    user2 = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'user1', 'user1_info', 'user2', 'user2_info', 'created_at', 'messages']
        read_only_fields = ['user1', 'user2', 'created_at']

    def create(self, validated_data):
        # ChatRoom 생성 시 user1과 user2를 설정
        # 여기서는 요청을 보낸 사용자를 user1으로, 다른 사용자를 user2로 가정
        user1 = self.context['request'].user
        user2_id = self.initial_data.get('user2') # 요청 본문에서 user2의 ID를 가져옴
        if not user2_id:
            raise serializers.ValidationError("user2 필드는 필수입니다.")
        
        # user2_id를 User 인스턴스로 변환
        try:
            user2 = User.objects.get(id=user2_id)
        except settings.AUTH_USER_MODEL.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 user2 ID입니다.")

        # user1과 user2의 순서를 정렬하여 중복 채팅방 생성 방지
        if user1.id < user2.id:
            validated_data['user1'] = user1
            validated_data['user2'] = user2
        else:
            validated_data['user1'] = user2
            validated_data['user2'] = user1

        # 이미 존재하는 채팅방인지 확인
        existing_chatroom = ChatRoom.objects.filter(
            user1=validated_data['user1'],
            user2=validated_data['user2']
        ).first()

        if existing_chatroom:
            return existing_chatroom # 이미 존재하는 채팅방 반환

        return super().create(validated_data)