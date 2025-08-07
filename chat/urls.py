from django.urls import path
from .views import ChatRoomListCreateView, ChatRoomRetrieveUpdateDestroyView, MessageListCreateView, chat_test_view

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('chatrooms/<int:pk>/', ChatRoomRetrieveUpdateDestroyView.as_view(), name='chatroom-retrieve-update-destroy'),
    path('chatrooms/<int:room_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('chat-test/', chat_test_view, name='chat_test'),
]