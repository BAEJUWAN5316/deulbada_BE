from django.contrib.auth import get_user_model
from django.db.models import Count, F
from rest_framework import serializers
from .models import Post, Comment

User = get_user_model()

class AuthorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","account_id","username","profile_image","is_farm_verified"]



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
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields

class PostWriteSerializer(serializers.ModelSerializer):
    images_add = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False), write_only=True, required=False
    )
    image_ids_delete = serializers.ListField(
        child=serializers.IntegerField(min_value=1), write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = ["title","content","image","images_add","image_ids_delete"]

    # def validate(self, attrs):
    #     add_list = self._get_add_list(attrs)
    #     del_list = self._get_del_list(attrs)
    #     if self.instance:
    #         current = (1 if self.instance.image else 0) + self.instance.images.count()
    #     else:
    #         current = 0
    #     incoming_single = 1 if attrs.get("image") else 0
    #     remaining = max(0, current - len(del_list))
    #     total_after = remaining + incoming_single + len(add_list)
    #     if total_after > 5:
    #         raise serializers.ValidationError("이미지는 최대 5장까지 업로드 가능합니다.")
    #     return attrs

    # def create(self, data):
    #     add = self._get_add_list(data, pop=True)
    #     post = Post.objects.create(**data)
    #     self._bulk_create_images(post, add)
    #     return post

    # def update(self, inst, data):
    #     add = self._get_add_list(data, pop=True)
    #     dels = self._get_del_list(data, pop=True)
    #     for k,v in data.items(): setattr(inst, k, v)
    #     inst.save()
    #     if dels: PostImage.objects.filter(post=inst, id__in=dels).delete()
    #     self._bulk_create_images(inst, add)
    #     return inst

    # def _get_add_list(self, data, pop=False):
    #     return (data.pop("images_add", []) if pop else data.get("images_add", [])) or []
    # def _get_del_list(self, data, pop=False):
    #     return (data.pop("image_ids_delete", []) if pop else data.get("image_ids_delete", [])) or []
    # def _bulk_create_images(self, post, files):
    #     if files:
    #         PostImage.objects.bulk_create([PostImage(post=post, image=f) for f in files])

class CommentSerializer(serializers.ModelSerializer):
    user = AuthorMiniSerializer(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Comment
        fields = ["id","post","user","content","parent","created_at","reply_count"]
        read_only_fields = ["post","user","reply_count"]