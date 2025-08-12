from django.contrib.auth import get_user_model
from django.db.models import Count, F
from rest_framework import serializers
from .models import Post, PostImage, Comment

User = get_user_model()

class AuthorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","account_id","username","profile_image","is_farm_verified"]

class PostImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = PostImage
        fields = ["id","url","created_at"]
    def get_url(self, obj):
        return getattr(obj.image, "url", None)

class _ImagesMixin(serializers.ModelSerializer):
    image_urls = serializers.SerializerMethodField()
    def get_image_urls(self, obj):
        urls = []
        if getattr(obj, "image", None):
            try: urls.append(obj.image.url)
            except Exception: pass
        for p in obj.images.all():
            try: urls.append(p.image.url)
            except Exception: pass
        return list(dict.fromkeys(urls))

class PostListSerializer(_ImagesMixin):
    author = AuthorMiniSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    author_is_farm_verified = serializers.BooleanField(read_only=True)
    class Meta:
        model = Post
        fields = ["id","author","title","content","created_at",
                  "like_count","comment_count","author_is_farm_verified","image_urls"]

class PostDetailSerializer(PostListSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["images"]

class PostWriteSerializer(serializers.ModelSerializer):
    # image1 = serializers.ImageField(required=False, write_only=True, help_text="추가 이미지 1")
    # image2 = serializers.ImageField(required=False, write_only=True, help_text="추가 이미지 2")
    # image3 = serializers.ImageField(required=False, write_only=True, help_text="추가 이미지 3")
    # image4 = serializers.ImageField(required=False, write_only=True, help_text="추가 이미지 4")
    images_add = serializers.ListField(
    child=serializers.ImageField(allow_empty_file=False),
    write_only=True,
    required=False,
    help_text="추가할 이미지들 (최대 4개)"
    )
    image_ids_delete = serializers.ListField(
    child=serializers.IntegerField(),
    write_only=True,
    required=False,
    help_text="삭제할 이미지 ID들"
    )
    class Meta:
        model = Post
        fields = ["title", "content", "image", "images_add", "image_ids_delete"]
    def validate(self, attrs):
        # 현재 이미지 개수 계산
        current_total = 0
        if self.instance:
            current_total = (1 if self.instance.image else 0) + self.instance.images.count()

    # 삭제할 개수
        delete_count = len(attrs.get('image_ids_delete', []))

    # 새로  추가할 개수
        new_main = 1 if attrs.get('image') else 0
        new_additional = len(attrs.get('images_add', []))

    # 최종 개수 계산
        if self.instance:
            # 수정: 현재 - 삭제 + 신규
            final_count = current_total - delete_count + new_main + new_additional
            # 메인 이미지 교체 시 개수 변화 없음
            if attrs.get('image') and self.instance.image:
                final_count -= 1
        else:
            # 생성: 신규만
            final_count = new_main + new_additional

        if final_count > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지 업로드 가능합니다.")

    # 추가 이미지만으로도 4개 제한
        if new_additional > 4:
            raise serializers.ValidationError("추가 이미지는 최대 4개까지 가능합니다.")

        return attrs
    
    def create(self, validated_data):
        images_add = validated_data.pop('images_add', [])
        validated_data.pop('image_ids_delete', [])  # 생성시에는 삭제 무시

        post = Post.objects.create(**validated_data)
        self._create_images(post, images_add)
        return post

    def update(self, instance, validated_data):
        images_add = validated_data.pop('images_add', [])
        image_ids_delete = validated_data.pop('image_ids_delete', [])

        # 게시글 정보 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        #  이미지 삭제
        if image_ids_delete:
            PostImage.objects.filter(post=instance, id__in=image_ids_delete).delete()

        # 새 이미지 추가
        self._create_images(instance, images_add)
        return instance

    def _create_images(self, post, image_files):
        """추가 이미지들을 PostImage로 저장"""
        if not image_files:
            return

        # 새 이미지들 생성
        new_images = [
            PostImage(post=post, image=img)
            for img in image_files
        ]
        PostImage.objects.bulk_create(new_images)



class CommentSerializer(serializers.ModelSerializer):
    user = AuthorMiniSerializer(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Comment
        fields = ["id","post","user","content","parent","created_at","reply_count"]
        read_only_fields = ["post","user","reply_count"]
