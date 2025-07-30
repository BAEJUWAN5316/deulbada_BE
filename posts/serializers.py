from rest_framework import serializers

class PostSerializer(serializers.Serializer):
    # 임시 Serializer, 실제 Post 모델에 따라 변경 필요
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
