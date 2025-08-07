"""
Django 커스텀 커맨드: load_dummy_data.py
- er2.txt 파일을 파싱해 더미 데이터를 안전하게 DB에 삽입함
- 각 모델별로 중복 생성 방지, 예외 처리, FK 안전성 확보
- 평문 비밀번호는 create_user를 통해 해싱하여 저장
- 모든 FK는 사전에 생성된 객체 딕셔너리를 참조
- 각 섹션 별로 실패 로그 출력 및 실행 지속
"""

import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from users.models import User, UserProfile, Report, Notification, Block # Report, Notification, Block 모델 임포트 추가
from categories.models import Category
from products.models import Product, ProductCategory
from posts.models import Post, Like, Comment
from chat.models import ChatRoom, Message
from django.db import transaction

class Command(BaseCommand):
    help = 'Loads dummy data from er2.txt into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[시작] 더미 데이터 로딩'))
        file_path = os.path.join(settings.BASE_DIR, 'er2.txt')

        if not os.path.exists(file_path):
            raise CommandError(f'er2.txt not found at {file_path}')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # FK 참조용 딕셔너리
        users = {}
        profiles = {}
        # follows = {}
        categories = {}
        products = {}
        product_categories = {}
        posts = {}
        comments = {}
        chatrooms = {}
        messages = {}

        def parse_value(key, val):
            val = val.strip("'\"")
            if val == 'True': return True
            if val == 'False': return False
            if val == 'None': return None
            if key in ['created_at', 'updated_at', 'date_joined', 'harvest_date']:
                try:
                    # 'Z'를 '+00:00'으로 대체하여 fromisoformat이 UTC를 올바르게 파싱하도록 함
                    return timezone.datetime.fromisoformat(val.replace('Z', '+00:00'))
                except Exception:
                    self.stdout.write(self.style.ERROR(f'\t⚠️ 날짜 파싱 실패: {val}'))
                    return timezone.now()
            if key in ['price', 'stock']:
                return int(val) if val.isdigit() else 0
            if val.startswith('[') and val.endswith(']'):
                # JSONField를 위한 리스트 파싱
                return [v.strip(" \"'") for v in val[1:-1].split(',') if v.strip()]
            return val

        def get_fk(ref, storage, label):
            if ref and ref.startswith('<FK_REFERENCE: '):
                key = ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                obj = storage.get(key)
                if not obj:
                    self.stdout.write(self.style.WARNING(f'\t⚠️ {label} FK not found: {key}'))
                return obj
            return None

        # --- User Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('User'))
        match = re.search(r'--- Dummy Data for User Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'User (\d+):\n(.*?)(?=(?:User \d+:)|$)', match.group(1), re.DOTALL)
            for user_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        if not User.objects.filter(account_id=fields['account_id']).exists():
                            user = User.objects.create_user(
                                account_id=fields['account_id'],
                                username=fields['username'],
                                email=fields['email'],
                                password=fields.get('password', 'default_password'), # 비밀번호 필드 추가
                            )
                            user.is_active = fields.get('is_active', True)
                            user.is_staff = fields.get('is_staff', False)
                            user.date_joined = fields.get('date_joined', timezone.now())
                            user.save()
                            self.stdout.write(self.style.SUCCESS(f'\t✅ Created User: {user.username}'))
                        else:
                            user = User.objects.get(account_id=fields['account_id'])
                            self.stdout.write(self.style.WARNING(f'\t⚠️ User exists: {user.username}'))
                        users[f'User {user_id}'] = user
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting User {user_id}: {e}'))

        # --- UserProfile Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('UserProfile'))
        match = re.search(r'--- Dummy Data for UserProfile Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'UserProfile (\d+):\n(.*?)(?=(?:UserProfile \d+:)|$)', match.group(1), re.DOTALL)
            for profile_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        user_obj = get_fk(fields.get('user'), users, 'User')
                        if user_obj:
                            if not UserProfile.objects.filter(user=user_obj).exists():
                                profile = UserProfile.objects.create(
                                    user=user_obj,
                                    profile_image=fields.get('profile_image'),
                                    bio=fields.get('bio'),
                                    is_farm_owner=fields.get('is_farm_owner', False),
                                    is_farm_verified=fields.get('is_farm_verified', False),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created UserProfile for {user_obj.username}'))
                            else:
                                profile = UserProfile.objects.get(user=user_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ UserProfile exists for {user_obj.username}'))
                            profiles[f'UserProfile {profile_id}'] = profile
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ User FK not found for UserProfile {profile_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting UserProfile {profile_id}: {e}'))

        # --- Report Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Report'))
        match = re.search(r'--- Dummy Data for Report Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Report (\d+):\n(.*?)(?=(?:Report \d+:)|$)', match.group(1), re.DOTALL)
            for report_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())

                try:
                    with transaction.atomic():
                        reporter_obj = get_fk(fields.get('reporter'), users, 'Reporter')
                        target_user_obj = get_fk(fields.get('target_user'), users, 'Target User')

                        if reporter_obj and target_user_obj:
                            if not Report.objects.filter(reporter=reporter_obj, target_user=target_user_obj, reason=fields['reason']).exists():
                                report = Report.objects.create(
                                    reporter=reporter_obj,
                                    target_user=target_user_obj,
                                    reason=fields.get('reason'),
                                    status=fields.get('status', 'pending'),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Report {report_id}: {reporter_obj.username} -> {target_user_obj.username}'))
                            else:
                                report = Report.objects.get(reporter=reporter_obj, target_user=target_user_obj, reason=fields['reason'])
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Report exists {report_id}: {reporter_obj.username} -> {target_user_obj.username}'))
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Report {report_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Report {report_id}: {e}'))

        # --- Notification Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Notification'))
        match = re.search(r'--- Dummy Data for Notification Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Notification (\d+):\n(.*?)(?=(?:Notification \d+:)|$)', match.group(1), re.DOTALL)
            for notif_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())

                try:
                    with transaction.atomic():
                        user_obj = get_fk(fields.get('user'), users, 'User')

                        if user_obj:
                            if not Notification.objects.filter(user=user_obj, message=fields['message']).exists():
                                notification = Notification.objects.create(
                                    user=user_obj,
                                    message=fields.get('message'),
                                    is_read=fields.get('is_read', False),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Notification {notif_id} for {user_obj.username}'))
                            else:
                                notification = Notification.objects.get(user=user_obj, message=fields['message'])
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Notification exists {notif_id} for {user_obj.username}'))
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Notification {notif_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Notification {notif_id}: {e}'))

        # --- Block Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Block'))
        match = re.search(r'--- Dummy Data for Block Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Block (\d+):\n(.*?)(?=(?:Block \d+:)|$)', match.group(1), re.DOTALL)
            for block_id, block_data in entries:
                fields = {}
                for line in block_data.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())

                try:
                    with transaction.atomic():
                        blocker_obj = get_fk(fields.get('blocker'), users, 'Blocker')
                        blocked_obj = get_fk(fields.get('blocked'), users, 'Blocked')

                        if blocker_obj and blocked_obj:
                            if not Block.objects.filter(blocker=blocker_obj, blocked=blocked_obj).exists():
                                block_instance = Block.objects.create(
                                    blocker=blocker_obj,
                                    blocked=blocked_obj,
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Block {block_id}: {blocker_obj.username} blocked {blocked_obj.username}'))
                            else:
                                block_instance = Block.objects.get(blocker=blocker_obj, blocked=blocked_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Block exists {block_id}: {blocker_obj.username} blocked {blocked_obj.username}'))
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Block {block_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Block {block_id}: {e}'))

        # --- Follow Model 처리 ---
# self.stdout.write(self.style.MIGRATE_HEADING('Follow'))
# match = re.search(r'--- Dummy Data for Follow Model ---\n(.*?)(?=--- Dummy Data for for|\Z)', content, re.DOTALL)
# if match:
#     entries = re.findall(r'Follow (\d+):\n(.*?)(?=(?:Follow \d+:)|$)', match.group(1), re.DOTALL)
#     for follow_id, block in entries:
#         fields = {}
#         for line in block.strip().split('\n'):
#             if ':' in line:
#                 k, v = line.split(':', 1)
#                 fields[k.strip()] = parse_value(k.strip(), v.strip())
#         
#         try:
#             with transaction.atomic():
#                 follower_obj = get_fk(fields.get('follower'), users, 'Follower')
#                 following_obj = get_fk(fields.get('following'), users, 'Following')
#
#                 if follower_obj and following_obj:
#                     # Assuming unique_together = ('follower', 'following')
#                     if not Follow.objects.filter(follower=follower_obj, following=following_obj).exists():
#                         follow = Follow.objects.create(
#                             follower=follower_obj,
#                             following=following_obj,
#                             created_at=fields.get('created_at', timezone.now()),
#                         )
#                         self.stdout.write(self.style.SUCCESS(f'\t✅ Created Follow: {follower_obj.username} -> {following_obj.username}'))
#                     else:
#                         follow = Follow.objects.get(follower=follower_obj, following=following_obj)
#                         self.stdout.write(self.style.WARNING(f'\t⚠️ Follow exists: {follower_obj.username} -> {following_obj.username}'))
#                     # follows[f'Follow {follow_id}'] = follow # Uncomment if Follow model is used as FK
#                 else:
#                     self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Follow {follow_id}'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Follow {follow_id}: {e}'))

        # --- Category Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Category'))
        match = re.search(r'--- Dummy Data for Category Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Category (\d+):\n(.*?)(?=(?:Category \d+:)|$)', match.group(1), re.DOTALL)
            for category_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        parent_obj = get_fk(fields.get('parent'), categories, 'Parent Category')
                        
                        if not Category.objects.filter(name=fields['name']).exists():
                            category = Category.objects.create(
                                name=fields['name'],
                                type=fields.get('type'),
                                icon_image=fields.get('icon_image'),
                                parent=parent_obj,
                                created_at=fields.get('created_at', timezone.now()),
                            )
                            self.stdout.write(self.style.SUCCESS(f'\t✅ Created Category: {category.name}'))
                        else:
                            category = Category.objects.get(name=fields['name'])
                            self.stdout.write(self.style.WARNING(f'\t⚠️ Category exists: {category.name}'))
                        categories[f'Category {category_id} ({category.name})'] = category
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Category {category_id}: {e}'))

        # --- Product Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Product'))
        match = re.search(r'--- Dummy Data for Product Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Product (\d+):\n(.*?)(?=(?:Product \d+:)|$)', match.group(1), re.DOTALL)
            for product_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        seller_obj = get_fk(fields.get('seller'), users, 'Seller')

                        if seller_obj:
                            if not Product.objects.filter(name=fields['name'], seller=seller_obj).exists():
                                product = Product.objects.create(
                                    seller=seller_obj,
                                    name=fields['name'],
                                    description=fields.get('description'),
                                    price=fields.get('price'),
                                    stock=fields.get('stock'),
                                    image_urls=fields.get('image_urls', []),
                                    variety=fields.get('variety'),
                                    region=fields.get('region'),
                                    harvest_date=fields.get('harvest_date'),
                                    product_url=fields.get('product_url'),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Product: {product.name}'))
                            else:
                                product = Product.objects.get(name=fields['name'], seller=seller_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Product exists: {product.name}'))
                            products[f'Product {product_id} ({product.name})'] = product
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Seller FK not found for Product {product_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Product {product_id}: {e}'))

        # --- ProductCategory Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('ProductCategory'))
        match = re.search(r'--- Dummy Data for ProductCategory Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'ProductCategory (\d+):\n(.*?)(?=(?:ProductCategory \d+:)|$)', match.group(1), re.DOTALL)
            for pc_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        product_obj = get_fk(fields.get('product'), products, 'Product')
                        category_obj = get_fk(fields.get('category'), categories, 'Category')

                        if product_obj and category_obj:
                            if not ProductCategory.objects.filter(product=product_obj, category=category_obj).exists():
                                pc = ProductCategory.objects.create(
                                    product=product_obj,
                                    category=category_obj,
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created ProductCategory: {product_obj.name} - {category_obj.name}'))
                            else:
                                pc = ProductCategory.objects.get(product=product_obj, category=category_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ ProductCategory exists: {product_obj.name} - {category_obj.name}'))
                            product_categories[f'ProductCategory {pc_id}'] = pc
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for ProductCategory {pc_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting ProductCategory {pc_id}: {e}'))

        # --- Post Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Post'))
        match = re.search(r'--- Dummy Data for Post Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Post (\d+):\n(.*?)(?=(?:Post \d+:)|$)', match.group(1), re.DOTALL)
            for post_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        author_obj = get_fk(fields.get('author'), users, 'Author')

                        if author_obj:
                            # Assuming content is unique enough for get_or_create, or you might need a better unique identifier
                            if not Post.objects.filter(author=author_obj, content=fields['content']).exists():
                                post = Post.objects.create(
                                    author=author_obj,
                                    content=fields['content'],
                                    image_urls=fields.get('image_urls', []),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Post: {post.content[:30]}...'))
                            else:
                                post = Post.objects.get(author=author_obj, content=fields['content'])
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Post exists: {post.content[:30]}...'))
                            posts[f'Post {post_id}'] = post
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Author FK not found for Post {post_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Post {post_id}: {e}'))

        # --- Like Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Like'))
        match = re.search(r'--- Dummy Data for Like Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Like (\d+):\n(.*?)(?=(?:Like \d+:)|$)', match.group(1), re.DOTALL)
            for like_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        user_obj = get_fk(fields.get('user'), users, 'User')
                        post_obj = get_fk(fields.get('post'), posts, 'Post')

                        if user_obj and post_obj:
                            if not Like.objects.filter(user=user_obj, post=post_obj).exists():
                                like = Like.objects.create(
                                    user=user_obj,
                                    post=post_obj,
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Like: {user_obj.username} -> Post {post_obj.id}'))
                            else:
                                like = Like.objects.get(user=user_obj, post=post_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Like exists: {user_obj.username} -> Post {post_obj.id}'))
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Like {like_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Like {like_id}: {e}'))

        # --- Comment Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Comment'))
        match = re.search(r'--- Dummy Data for Comment Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Comment (\d+):\n(.*?)(?=(?:Comment \d+:)|$)', match.group(1), re.DOTALL)
            for comment_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        post_obj = get_fk(fields.get('post'), posts, 'Post')
                        user_obj = get_fk(fields.get('user'), users, 'User')
                        parent_obj = get_fk(fields.get('parent'), comments, 'Parent Comment')

                        if post_obj and user_obj:
                            # Assuming content is unique enough for get_or_create within a post by a user
                            if not Comment.objects.filter(post=post_obj, user=user_obj, content=fields['content']).exists():
                                comment = Comment.objects.create(
                                    post=post_obj,
                                    user=user_obj,
                                    content=fields['content'],
                                    parent=parent_obj,
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Comment: {comment.content[:30]}...'))
                                comments[f'Comment {comment_id}'] = comment
                            else:
                                comment = Comment.objects.get(post=post_obj, user=user_obj, content=fields['content'])
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Comment exists: {comment.content[:30]}...'))
                                comments[f'Comment {comment_id}'] = comment # Ensure it's added to dict even if exists
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Comment {comment_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Comment {comment_id}: {e}'))

        # --- ChatRoom Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('ChatRoom'))
        match = re.search(r'--- Dummy Data for ChatRoom Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'ChatRoom (\d+):\n(.*?)(?=(?:ChatRoom \d+:)|$)', match.group(1), re.DOTALL)
            for room_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        user1_obj = get_fk(fields.get('user1'), users, 'User1')
                        user2_obj = get_fk(fields.get('user2'), users, 'User2')

                        if user1_obj and user2_obj:
                            # Ensure consistent order for get_or_create to avoid duplicates (user1, user2) vs (user2, user1)
                            if user1_obj.pk > user2_obj.pk:
                                user1_obj, user2_obj = user2_obj, user1_obj

                            if not ChatRoom.objects.filter(user1=user1_obj, user2=user2_obj).exists():
                                room = ChatRoom.objects.create(
                                    user1=user1_obj,
                                    user2=user2_obj,
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created ChatRoom between {user1_obj.username} and {user2_obj.username}'))
                            else:
                                room = ChatRoom.objects.get(user1=user1_obj, user2=user2_obj)
                                self.stdout.write(self.style.WARNING(f'\t⚠️ ChatRoom exists between {user1_obj.username} and {user2_obj.username}'))
                            chatrooms[f'ChatRoom {room_id}'] = room
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for ChatRoom {room_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting ChatRoom {room_id}: {e}'))

        # --- Message Model 처리 ---
        self.stdout.write(self.style.MIGRATE_HEADING('Message'))
        match = re.search(r'--- Dummy Data for Message Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if match:
            entries = re.findall(r'Message (\d+):\n(.*?)(?=(?:Message \d+:)|$)', match.group(1), re.DOTALL)
            for msg_id, block in entries:
                fields = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fields[k.strip()] = parse_value(k.strip(), v.strip())
                
                try:
                    with transaction.atomic():
                        room_obj = get_fk(fields.get('room'), chatrooms, 'ChatRoom')
                        sender_obj = get_fk(fields.get('sender'), users, 'Sender')

                        if room_obj and sender_obj:
                            # Assuming content and sender are unique enough for get_or_create within a room
                            if not Message.objects.filter(room=room_obj, sender=sender_obj, content=fields['content']).exists():
                                message = Message.objects.create(
                                    room=room_obj,
                                    sender=sender_obj,
                                    content=fields['content'],
                                    image_url=fields.get('image_url'),
                                    is_read=fields.get('is_read', False),
                                    created_at=fields.get('created_at', timezone.now()),
                                )
                                self.stdout.write(self.style.SUCCESS(f'\t✅ Created Message: {message.content[:30]}...'))
                            else:
                                message = Message.objects.get(room=room_obj, sender=sender_obj, content=fields['content'])
                                self.stdout.write(self.style.WARNING(f'\t⚠️ Message exists: {message.content[:30]}...'))
                        else:
                            self.stdout.write(self.style.ERROR(f'\t❌ Missing FK for Message {msg_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'\t❌ Error creating/getting Message {msg_id}: {e}'))

        self.stdout.write(self.style.SUCCESS('[완료] 더미 데이터 로딩 끝'))
