from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_rooms_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_rooms_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # user1과 user2의 조합이 유니크하도록 설정 (순서에 상관없이 유니크하도록 하려면 추가 로직 필요)
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True) # 이미지 메시지 (선택)
    is_read = models.BooleanField(default=False) # 읽음 여부
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.room.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
