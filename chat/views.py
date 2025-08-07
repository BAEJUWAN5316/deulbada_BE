from rest_framework import generics, permissions
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied # PermissionDenied import 추가

class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 현재 사용자가 참여하고 있는 채팅방만 보여줍니다.
        return ChatRoom.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user))

    def perform_create(self, serializer):
        # Serializer의 create 메서드에서 user1, user2 설정 및 중복 처리
        serializer.save(request=self.request) # request 객체를 context로 전달하여 serializer에서 사용

class ChatRoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated] # 인증된 사용자만 접근 가능

    def get_queryset(self):
        # 현재 사용자가 참여하고 있는 채팅방만 조회 가능
        return ChatRoom.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user))

    def get_object(self):
        obj = super().get_object()
        # 요청 메서드가 쓰기(PUT, PATCH, DELETE)인 경우에만 소유자 확인
        if self.request.method not in permissions.SAFE_METHODS:
            # 현재 사용자가 채팅방의 user1 또는 user2인지 확인
            if not (obj.user1 == self.request.user or obj.user2 == self.request.user):
                raise PermissionDenied("이 채팅방에 대한 수정/삭제 권한이 없습니다.")
        return obj

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 특정 채팅방의 메시지만 보여줍니다.
        chat_room_id = self.kwargs['room_id'] # URL 패턴 변경에 따라 kwargs 키 변경
        return Message.objects.filter(room_id=chat_room_id)

    def perform_create(self, serializer):
        # 메시지 생성 시 현재 요청을 보낸 사용자를 발신자로 설정
        chat_room_id = self.kwargs['room_id'] # URL 패턴 변경에 따라 kwargs 키 변경
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        serializer.save(sender=self.request.user, room=chat_room)

from django.shortcuts import render

def chat_test_view(request):
    return render(request, 'chat/chat_test.html')