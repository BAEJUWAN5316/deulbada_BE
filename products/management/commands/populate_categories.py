from django.core.management.base import BaseCommand
from categories.models import Category

class Command(BaseCommand):
    help = 'Populates the database with initial category data.'

    def handle(self, *args, **options):
        self.stdout.write("Populating categories...")

        # Agricultural Categories
        for cat_name in Category.AGRICULTURAL_CATEGORIES:
            Category.objects.get_or_create(name=cat_name, defaults={'type': 'agricultural'})
            self.stdout.write(self.style.SUCCESS(f"Created/found: {cat_name} (Agricultural)"))

        # Fishing Categories
        for cat_name in Category.FISHING_CATEGORIES:
            Category.objects.get_or_create(name=cat_name, defaults={'type': 'fishing'})
            self.stdout.write(self.style.SUCCESS(f"Created/found: {cat_name} (Fishing)"))

        self.stdout.write(self.style.SUCCESS(f"Total categories now: {Category.objects.count()}"))
        self.stdout.write(self.style.SUCCESS('Category population complete.'))