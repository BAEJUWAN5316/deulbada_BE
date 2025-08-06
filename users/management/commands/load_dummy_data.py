import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from users.models import User, UserProfile
from categories.models import Category
from products.models import Product, ProductCategory
from posts.models import Post, Like, Comment
from chat.models import ChatRoom, Message

class Command(BaseCommand):
    help = 'Loads dummy data from er2.txt into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load dummy data...'))

        file_path = os.path.join(settings.BASE_DIR, 'er2.txt')

        if not os.path.exists(file_path):
            raise CommandError(f'er2.txt not found at {file_path}')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Store created objects for FK references
        created_users = {}
        created_categories = {}
        created_products = {}
        created_posts = {}
        created_chatrooms = {}
        created_comments = {} # For parent comment reference

        # --- User Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading User Data...'))
        user_data_match = re.search(r'--- Dummy Data for User Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if user_data_match:
            user_section = user_data_match.group(1).strip()
            user_entries = re.findall(r'User (\d+):\n(.*?)(?=(?:User \d+:)|$)', user_section, re.DOTALL)
            for user_id_str, data_str in user_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'True':
                            data[key] = True
                        elif value == 'False':
                            data[key] = False
                        elif value == 'None':
                            data[key] = None
                        elif key in ['date_joined']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"") # Remove quotes if present

                try:
                    user, created = User.objects.get_or_create(
                        account_id=data['account_id'],
                        defaults={
                            'username': data['username'],
                            'email': data['email'],
                            'password': data['password'], # In a real app, hash this!
                            'is_active': data['is_active'],
                            'is_staff': data['is_staff'],
                            'date_joined': data['date_joined'],
                        }
                    )
                    created_users[f'User {user_id_str}'] = user
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created User: {user.username}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'User already exists: {user.username}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating User {user_id_str}: {e}'))

        # --- UserProfile Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading UserProfile Data...'))
        userprofile_data_match = re.search(r'--- Dummy Data for UserProfile Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if userprofile_data_match:
            userprofile_section = userprofile_data_match.group(1).strip()
            userprofile_entries = re.findall(r'UserProfile (\d+):\n(.*?)(?=(?:UserProfile \d+:)|$)', userprofile_section, re.DOTALL)
            for profile_id_str, data_str in userprofile_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'True':
                            data[key] = True
                        elif value == 'False':
                            data[key] = False
                        elif value == 'None':
                            data[key] = None
                        elif key in ['created_at', 'updated_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                user_ref = data.get('user')
                if user_ref and user_ref.startswith('<FK_REFERENCE: '):
                    user_key = user_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    user_obj = created_users.get(user_key)
                    if user_obj:
                        try:
                            user_profile, created = UserProfile.objects.get_or_create(
                                user=user_obj,
                                defaults={
                                    'profile_image': data.get('profile_image'),
                                    'bio': data.get('bio'),
                                    'is_farm_owner': data.get('is_farm_owner'),
                                    'is_farm_verified': data.get('is_farm_verified'),
                                    'created_at': data.get('created_at'),
                                    'updated_at': data.get('updated_at'),
                                }
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user_obj.username}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'UserProfile already exists for {user_obj.username}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error creating UserProfile {profile_id_str} for {user_obj.username}: {e}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'User reference not found for UserProfile {profile_id_str}: {user_key}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Invalid user reference for UserProfile {profile_id_str}: {user_ref}'))

        # --- Follow Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Follow Data...'))
        follow_data_match = re.search(r'--- Dummy Data for Follow Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if follow_data_match:
            follow_section = follow_data_match.group(1).strip()
            follow_entries = re.findall(r'Follow (\d+):\n(.*?)(?=(?:Follow \d+:)|$)', follow_section, re.DOTALL)
            for follow_id_str, data_str in follow_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'None':
                            data[key] = None
                        elif key in ['created_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                follower_ref = data.get('follower')
                following_ref = data.get('following')

                follower_obj = None
                if follower_ref and follower_ref.startswith('<FK_REFERENCE: '):
                    follower_key = follower_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    follower_obj = created_users.get(follower_key)
                
                following_obj = None
                if following_ref and following_ref.startswith('<FK_REFERENCE: '):
                    following_key = following_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    following_obj = created_users.get(following_key)

                if follower_obj and following_obj:
                    try:
                        # Assuming Follow model is in users.models or a related app
                        # You might need to import it: from users.models import Follow
                        # For now, I'll assume it's in users.models for demonstration
                        from users.models import Follow # Import here for now, move to top later
                        follow, created = Follow.objects.get_or_create(
                            follower=follower_obj,
                            following=following_obj,
                            defaults={
                                'created_at': data.get('created_at'),
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Follow: {follower_obj.username} -> {following_obj.username}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Follow already exists: {follower_obj.username} -> {following_obj.username}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Follow {follow_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing follower or following reference for Follow {follow_id_str}'))

        # --- Category Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Category Data...'))
        category_data_match = re.search(r'--- Dummy Data for Category Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if category_data_match:
            category_section = category_data_match.group(1).strip()
            category_entries = re.findall(r'Category (\d+):\n(.*?)(?=(?:Category \d+:)|$)', category_section, re.DOTALL)
            for category_id_str, data_str in category_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'None':
                            data[key] = None
                        elif key in ['created_at', 'updated_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                parent_ref = data.get('parent')
                parent_obj = None
                if parent_ref and parent_ref.startswith('<FK_REFERENCE: '):
                    parent_key_match = re.search(r'<FK_REFERENCE: (Category \d+)', parent_ref)
                    if parent_key_match:
                        parent_key = parent_key_match.group(1)
                        parent_obj = created_categories.get(parent_key)
                    else:
                        self.stdout.write(self.style.WARNING(f'Could not parse parent FK_REFERENCE for Category {category_id_str}: {parent_ref}'))

                try:
                    category, created = Category.objects.get_or_create(
                        name=data['name'],
                        defaults={
                            'type': data.get('type'),
                            'icon_image': data.get('icon_image'),
                            'parent': parent_obj,
                            'created_at': data.get('created_at'),
                            'updated_at': data.get('updated_at'),
                        }
                    )
                    created_categories[f'Category {category_id_str} ({data["name"]})'] = category
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created Category: {category.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating Category {category_id_str}: {e}'))

        # --- Product Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Product Data...'))
        product_data_match = re.search(r'--- Dummy Data for Product Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if product_data_match:
            product_section = product_data_match.group(1).strip()
            product_entries = re.findall(r'Product (\d+):\n(.*?)(?=(?:Product \d+:)|$)', product_section, re.DOTALL)
            for product_id_str, data_str in product_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'None':
                            data[key] = None
                        elif value.startswith('[') and value.endswith(']'):
                            data[key] = [s.strip('"') for s in value[1:-1].split(',')] if value[1:-1] else []
                        elif key in ['harvest_date']:
                            data[key] = timezone.datetime.fromisoformat(value).date() if value != 'None' else None
                        elif key in ['created_at', 'updated_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        elif key in ['price', 'stock']:
                            data[key] = int(value)
                        else:
                            data[key] = value.strip("'"")

                seller_ref = data.get('seller')
                seller_obj = None
                if seller_ref and seller_ref.startswith('<FK_REFERENCE: '):
                    seller_key = seller_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    seller_obj = created_users.get(seller_key)

                if seller_obj:
                    try:
                        product, created = Product.objects.get_or_create(
                            name=data['name'],
                            seller=seller_obj,
                            defaults={
                                'description': data.get('description'),
                                'price': data.get('price'),
                                'stock': data.get('stock'),
                                'image_urls': data.get('image_urls'),
                                'variety': data.get('variety'),
                                'region': data.get('region'),
                                'harvest_date': data.get('harvest_date'),
                                'product_url': data.get('product_url'),
                                'created_at': data.get('created_at'),
                                'updated_at': data.get('updated_at'),
                            }
                        )
                        created_products[f'Product {product_id_str} ({data["name"]})'] = product
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Product: {product.name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Product {product_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing seller reference for Product {product_id_str}'))

        # --- ProductCategory Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading ProductCategory Data...'))
        productcategory_data_match = re.search(r'--- Dummy Data for ProductCategory Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if productcategory_data_match:
            productcategory_section = productcategory_data_match.group(1).strip()
            productcategory_entries = re.findall(r'ProductCategory (\d+):\n(.*?)(?=(?:ProductCategory \d+:)|$)', productcategory_section, re.DOTALL)
            for pc_id_str, data_str in productcategory_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        data[key] = value.strip("'"")

                product_ref = data.get('product')
                category_ref = data.get('category')

                product_obj = None
                if product_ref and product_ref.startswith('<FK_REFERENCE: '):
                    product_key_match = re.search(r'<FK_REFERENCE: (Product \d+ \(.*\))>', product_ref)
                    if product_key_match:
                        product_key = product_key_match.group(1)
                        product_obj = created_products.get(product_key)
                    else:
                        self.stdout.write(self.style.WARNING(f'Could not parse product FK_REFERENCE for ProductCategory {pc_id_str}: {product_ref}'))

                category_obj = None
                if category_ref and category_ref.startswith('<FK_REFERENCE: '):
                    category_key_match = re.search(r'<FK_REFERENCE: (Category \d+ \(.*\))>', category_ref)
                    if category_key_match:
                        category_key = category_key_match.group(1)
                        category_obj = created_categories.get(category_key)
                    else:
                        self.stdout.write(self.style.WARNING(f'Could not parse category FK_REFERENCE for ProductCategory {pc_id_str}: {category_ref}'))

                if product_obj and category_obj:
                    try:
                        product_category, created = ProductCategory.objects.get_or_create(
                            product=product_obj,
                            category=category_obj,
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created ProductCategory: {product_obj.name} - {category_obj.name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'ProductCategory already exists: {product_obj.name} - {category_obj.name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating ProductCategory {pc_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing product or category reference for ProductCategory {pc_id_str}'))

        # --- Post Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Post Data...'))
        post_data_match = re.search(r'--- Dummy Data for Post Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if post_data_match:
            post_section = post_data_match.group(1).strip()
            post_entries = re.findall(r'Post (\d+):\n(.*?)(?=(?:Post \d+:)|$)', post_section, re.DOTALL)
            for post_id_str, data_str in post_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value.startswith('[') and value.endswith(']'):
                            data[key] = [s.strip('"') for s in value[1:-1].split(',')] if value[1:-1] else []
                        elif key in ['created_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                author_ref = data.get('author')
                author_obj = None
                if author_ref and author_ref.startswith('<FK_REFERENCE: '):
                    author_key = author_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    author_obj = created_users.get(author_key)

                if author_obj:
                    try:
                        post, created = Post.objects.get_or_create(
                            author=author_obj,
                            content=data['content'],
                            defaults={
                                'image_urls': data.get('image_urls'),
                                'created_at': data.get('created_at'),
                            }
                        )
                        created_posts[f'Post {post_id_str}'] = post
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Post: {post.content[:30]}...'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Post already exists: {post.content[:30]}...'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Post {post_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing author reference for Post {post_id_str}'))

        # --- Like Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Like Data...'))
        like_data_match = re.search(r'--- Dummy Data for Like Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if like_data_match:
            like_section = like_data_match.group(1).strip()
            like_entries = re.findall(r'Like (\d+):\n(.*?)(?=(?:Like \d+:)|$)', like_section, re.DOTALL)
            for like_id_str, data_str in like_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['created_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                user_ref = data.get('user')
                post_ref = data.get('post')

                user_obj = None
                if user_ref and user_ref.startswith('<FK_REFERENCE: '):
                    user_key = user_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    user_obj = created_users.get(user_key)
                
                post_obj = None
                if post_ref and post_ref.startswith('<FK_REFERENCE: '):
                    post_key = post_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    post_obj = created_posts.get(post_key)

                if user_obj and post_obj:
                    try:
                        like, created = Like.objects.get_or_create(
                            user=user_obj,
                            post=post_obj,
                            defaults={
                                'created_at': data.get('created_at'),
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Like: {user_obj.username} -> Post {post_obj.id}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Like already exists: {user_obj.username} -> Post {post_obj.id}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Like {like_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing user or post reference for Like {like_id_str}'))

        # --- Comment Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Comment Data...'))
        comment_data_match = re.search(r'--- Dummy Data for Comment Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if comment_data_match:
            comment_section = comment_data_match.group(1).strip()
            comment_entries = re.findall(r'Comment (\d+):\n(.*?)(?=(?:Comment \d+:)|$)', comment_section, re.DOTALL)
            for comment_id_str, data_str in comment_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'None':
                            data[key] = None
                        elif key in ['created_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                post_ref = data.get('post')
                user_ref = data.get('user')
                parent_ref = data.get('parent')

                post_obj = None
                if post_ref and post_ref.startswith('<FK_REFERENCE: '):
                    post_key = post_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    post_obj = created_posts.get(post_key)
                
                user_obj = None
                if user_ref and user_ref.startswith('<FK_REFERENCE: '):
                    user_key = user_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    user_obj = created_users.get(user_key)

                parent_comment_obj = None
                if parent_ref and parent_ref.startswith('<FK_REFERENCE: '):
                    parent_comment_key = parent_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    parent_comment_obj = created_comments.get(parent_comment_key)

                if post_obj and user_obj:
                    try:
                        comment, created = Comment.objects.get_or_create(
                            post=post_obj,
                            user=user_obj,
                            content=data['content'],
                            defaults={
                                'parent': parent_comment_obj,
                                'created_at': data.get('created_at'),
                            }
                        )
                        created_comments[f'Comment {comment_id_str}'] = comment
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Comment: {comment.content[:30]}...'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Comment already exists: {comment.content[:30]}...'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Comment {comment_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing post or user reference for Comment {comment_id_str}'))

        # --- ChatRoom Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading ChatRoom Data...'))
        chatroom_data_match = re.search(r'--- Dummy Data for ChatRoom Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if chatroom_data_match:
            chatroom_section = chatroom_data_match.group(1).strip()
            chatroom_entries = re.findall(r'ChatRoom (\d+):\n(.*?)(?=(?:ChatRoom \d+:)|$)', chatroom_section, re.DOTALL)
            for room_id_str, data_str in chatroom_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['created_at', 'updated_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                user1_ref = data.get('user1')
                user2_ref = data.get('user2')

                user1_obj = None
                if user1_ref and user1_ref.startswith('<FK_REFERENCE: '):
                    user1_key = user1_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    user1_obj = created_users.get(user1_key)
                
                user2_obj = None
                if user2_ref and user2_ref.startswith('<FK_REFERENCE: '):
                    user2_key = user2_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    user2_obj = created_users.get(user2_key)

                if user1_obj and user2_obj:
                    try:
                        chatroom, created = ChatRoom.objects.get_or_create(
                            user1=user1_obj,
                            user2=user2_obj,
                            defaults={
                                'created_at': data.get('created_at'),
                                'updated_at': data.get('updated_at'),
                            }
                        )
                        created_chatrooms[f'ChatRoom {room_id_str}'] = chatroom
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created ChatRoom between {user1_obj.username} and {user2_obj.username}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'ChatRoom already exists between {user1_obj.username} and {user2_obj.username}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating ChatRoom {room_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing user1 or user2 reference for ChatRoom {room_id_str}'))

        # --- Message Model Data ---
        self.stdout.write(self.style.MIGRATE_HEADING('Loading Message Data...'))
        message_data_match = re.search(r'--- Dummy Data for Message Model ---\n(.*?)(?=--- Dummy Data for|\Z)', content, re.DOTALL)
        if message_data_match:
            message_section = message_data_match.group(1).strip()
            message_entries = re.findall(r'Message (\d+):\n(.*?)(?=(?:Message \d+:)|$)', message_section, re.DOTALL)
            for msg_id_str, data_str in message_entries:
                data = {}
                for line in data_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value == 'True':
                            data[key] = True
                        elif value == 'False':
                            data[key] = False
                        elif value == 'None':
                            data[key] = None
                        elif key in ['created_at']:
                            data[key] = timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            data[key] = value.strip("'"")

                room_ref = data.get('room')
                sender_ref = data.get('sender')

                room_obj = None
                if room_ref and room_ref.startswith('<FK_REFERENCE: '):
                    room_key = room_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    room_obj = created_chatrooms.get(room_key)
                
                sender_obj = None
                if sender_ref and sender_ref.startswith('<FK_REFERENCE: '):
                    sender_key = sender_ref.replace('<FK_REFERENCE: ', '').replace('>', '')
                    sender_obj = created_users.get(sender_key)

                if room_obj and sender_obj:
                    try:
                        message, created = Message.objects.get_or_create(
                            room=room_obj,
                            sender=sender_obj,
                            content=data['content'],
                            defaults={
                                'image_url': data.get('image_url'),
                                'is_read': data.get('is_read'),
                                'created_at': data.get('created_at'),
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Message: {message.content[:30]}...'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Message already exists: {message.content[:30]}...'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating Message {msg_id_str}: {e}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Missing room or sender reference for Message {msg_id_str}'))


        self.stdout.write(self.style.SUCCESS('Finished loading dummy data.'))