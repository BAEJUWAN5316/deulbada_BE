from rest_framework import generics, filters, permissions
from .models import User, Report
from .serializers import UserSerializer, ReportSerializer, UserDetailSerializer
from rest_framework.permissions import IsAuthenticated

# 🔍 유저 검색
class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'account_id']
    permission_classes = [permissions.IsAuthenticated]

# 📝 내가 쓴 게시글 조회
class MyPostsView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# 🚨 유저 신고
class ReportCreateAPIView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)