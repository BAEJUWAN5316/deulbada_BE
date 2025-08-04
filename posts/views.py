from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post
from .serializers import PostCreateSerializer
from rest_framework import generics
from .models import Post
from .serializers import PostListSerializer

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostListSerializer

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)

        return Response({
            "message": "게시글 작성 완료!",
            "id": post.id,
            "author": post.author.username,
            "content": post.content,
            "image_urls": post.image_urls or []
        }, status=status.HTTP_201_CREATED)
