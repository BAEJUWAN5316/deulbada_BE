# chat/views.py
from rest_framework import generics, permissions
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.db.models import Q

class ChatRoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))

class ChatRoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))

class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.select_related("room", "sender")
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        # 메시지 생성 시 현재 요청을 보낸 사용자를 발신자로 설정
        chat_room_id = self.kwargs['room_id'] # URL 패턴 변경에 따라 kwargs 키 변경
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        serializer.save(sender=self.request.user, room=chat_room)

from django.shortcuts import render

def chat_test_view(request):
    return render(request, 'chat/chat_test.html')