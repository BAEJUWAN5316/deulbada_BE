from rest_framework import generics
from posts.models import Post
from posts.serializers import PostSerializer

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
