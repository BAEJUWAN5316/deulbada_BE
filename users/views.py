from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import (
    UserSerializer,
    ReportSerializer,
    UserDetailSerializer,
    SignupSerializer,
)

# 🔍 유저 검색
class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'account_id']
    permission_classes = [IsAuthenticated]

# 📝 내가 쓴 게시글 조회
class MyPostsView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# 🚨 유저 신고
class ReportCreateAPIView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

# 🆕 회원가입
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "회원가입 성공",
                "user_id": user.id,
                "is_farm_owner": getattr(getattr(user, "profile", None), "is_farm_owner", False),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
