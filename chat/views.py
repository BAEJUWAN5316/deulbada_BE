# chat/views.py
from rest_framework import generics, permissions
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

class ChatRoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

class ChatRoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.select_related("room", "sender")
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
