from django.urls import path
from .views import ChatRoomListCreateView, ChatRoomRetrieveUpdateDestroyView, MessageListCreateView

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('chatrooms/<int:pk>/', ChatRoomRetrieveUpdateDestroyView.as_view(), name='chatroom-retrieve-update-destroy'),
    path('chatrooms/<int:room_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
]