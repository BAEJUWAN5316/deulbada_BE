# users/views.py
from rest_framework import generics, permissions
from .models import User
from .serializers import MyProfileSerializer

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
