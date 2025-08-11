import re
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = 'Loads dummy data from er2.txt into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear all existing data before loading new data')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing all existing data...'))
            self._clear_all_data()
            self.stdout.write(self.style.SUCCESS('All existing data cleared.'))

        file_path = 'er2.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except FileNotFoundError:
            raise CommandError(f'File "{file_path}" does not exist.')

        self.stdout.write(self.style.SUCCESS(f'Parsing dummy data from {file_path}...'))
        parsed_data = self._parse_dummy_data(file_content)
        self.stdout.write(self.style.SUCCESS('Dummy data parsed successfully.'))

        self.stdout.write(self.style.SUCCESS('Loading data into database...'))
        self._load_data(parsed_data)
        self.stdout.write(self.style.SUCCESS('Dummy data loaded successfully!'))

    def _clear_all_data(self):
        model_deletion_order = [
            'Follow', 'Comment', 'Like', 'Message',
            'ChatRoom', 'Product', 'Post', 'UserProfile', 'Category', 'User'
        ]

        for model_name in model_deletion_order:
            try:
                Model = self._get_model_by_name(model_name)
                if Model:
                    self.stdout.write(f'Deleting all {model_name} objects...')
                    Model.objects.all().delete()
                else:
                    self.stdout.write(self.style.WARNING(f'Could not find model {model_name} for deletion.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting {model_name} objects: {e}'))
                raise

    def _get_model_by_name(self, model_name):
        if model_name in ['User', 'UserProfile', 'Follow']:
            return apps.get_model('users', model_name)
        elif model_name == 'Category':
            return apps.get_model('categories', model_name)
        elif model_name in ['ChatRoom', 'Message']:
            return apps.get_model('chat', model_name)
        elif model_name in ['Post', 'Like', 'Comment']:
            return apps.get_model('posts', model_name)
        elif model_name == 'Product':
            return apps.get_model('products', model_name)
        return None

    def _parse_dummy_data(self, file_content):
        data = {}
        sections = re.split(r'---\s*Dummy Data for (\w+) Model\s*---', file_content)

        for i in range(1, len(sections), 2):
            model_name = sections[i].strip()
            model_data_str = sections[i + 1].strip()
            data[model_name] = []

            instance_blocks = re.split(r'(\w+)\s+(\d+):\n', model_data_str)

            for j in range(1, len(instance_blocks), 3):
                instance_id = int(instance_blocks[j + 1].strip())
                fields_str = instance_blocks[j + 2].strip()

                instance_data = {'_id': instance_id}

                for line in fields_str.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if value == 'None':
                        instance_data[key] = None
                    elif value.startswith('<FK_REFERENCE:'):
                        fk_ref = value.replace('<FK_REFERENCE:', '').replace('>', '').strip()
                        instance_data[key] = f"<FK_REFERENCE:{fk_ref}>"
                    elif value.startswith('[') and value.endswith(']'):
                        instance_data[key] = [item.strip().strip('"') for item in value[1:-1].split(',') if item.strip()]
                    elif value.lower() == 'true':
                        instance_data[key] = True
                    elif value.lower() == 'false':
                        instance_data[key] = False
                    elif re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
                        dt_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                        instance_data[key] = make_aware(dt_obj)
                    elif re.match(r'\d{4}-\d{2}-\d{2}', value):
                        instance_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                    elif value.isdigit():
                        instance_data[key] = int(value)
                    else:
                        instance_data[key] = value

                data[model_name].append(instance_data)
        return data

    def _load_data(self, parsed_data):
        created_instances = {}
        model_creation_order = [
            'User', 'Category', 'UserProfile', 'ChatRoom', 'Post',
            'Message', 'Like', 'Comment', 'Product', 'Follow'
        ]

        # 1차: 인스턴스 생성
        for model_name in model_creation_order:
            if model_name not in parsed_data:
                continue

            Model = self._get_model_by_name(model_name)
            if not Model:
                self.stdout.write(self.style.WARNING(f'Skipping unknown model: {model_name}'))
                continue

            self.stdout.write(f'Creating {model_name} instances...')
            created_instances[model_name] = {}
            for item_data_original in parsed_data[model_name]:
                item_data = item_data_original.copy()
                pk = item_data.pop('_id')
                data_for_creation = {}

                for key, value in item_data.items():
                    if isinstance(value, str) and value.startswith('<FK_REFERENCE:'):
                        continue
                    data_for_creation[key] = value

                try:
                    if model_name == 'User':
                        instance = Model.objects.create_user(
                            email=data_for_creation.get('email', f'user{pk}@test.com'),
                            password='testpass123',
                            **{k: v for k, v in data_for_creation.items() if k not in ['email', 'password']}
                        )
                    else:
                        instance = Model.objects.create(**data_for_creation)
                    created_instances[model_name][pk] = instance
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating {model_name} {pk}: {e}'))
                    raise

        # 2차: FK/M2M 매핑
        self.stdout.write('Resolving remaining foreign key and ManyToMany relationships...')
        for model_name in model_creation_order:
            if model_name not in parsed_data:
                continue

            Model = self._get_model_by_name(model_name)
            if not Model:
                continue

            for item_data_original in parsed_data[model_name]:
                pk = item_data_original['_id']
                instance = created_instances[model_name][pk]

                for key, value in item_data_original.items():
                    if isinstance(value, str):
                        if value.startswith('<FK_REFERENCE:'):
                            ref_model_name, ref_pk = value.replace('<FK_REFERENCE:', '').replace('>', '').split()
                            ref_pk = int(ref_pk)
                            related_instance = created_instances.get(ref_model_name, {}).get(ref_pk)
                            if related_instance:
                                setattr(instance, key, related_instance)
                        else:
                            # FK가 문자열로만 온 경우 (예: "User 1")
                            if key == 'user' and model_name == 'UserProfile':
                                related_instance = None
                                for u in created_instances.get('User', {}).values():
                                    if u.username == value or getattr(u, 'account_id', None) == value:
                                        related_instance = u
                                        break
                                if related_instance:
                                    setattr(instance, key, related_instance)

                instance.save()

        self.stdout.write(self.style.SUCCESS('All data loaded and relationships resolved.'))
