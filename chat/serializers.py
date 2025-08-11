# chat/serializers.py
from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    # 유저 정보는 중첩 직렬화 대신 PK만 노출
    user1 = serializers.PrimaryKeyRelatedField(read_only=True)
    user2 = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "user1", "user2", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    # sender는 PK만, room은 PK로 입력받음
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "content", "image_url", "is_read", "created_at"]
        read_only_fields = ["is_read", "created_at"]
