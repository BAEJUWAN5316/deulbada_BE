from rest_framework import generics, permissions
from django.db.models import Q
from .models import User
from .serializers import UserSearchSerializer

class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(
            Q(account_id__icontains=query) | Q(username__icontains=query)
        ).order_by('username')
