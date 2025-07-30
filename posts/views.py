from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer

class PostListView(APIView):
    def get(self, request, format=None):
        # 임시 데이터
        posts = [
            {'id': 1, 'title': '첫 번째 게시글', 'content': '안녕하세요.'},
            {'id': 2, 'title': '두 번째 게시글', 'content': '반갑습니다.'},
        ]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # 실제 모델 저장 로직은 여기에
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)