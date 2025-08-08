from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FarmerProfile, User


@receiver(post_save, sender=User)
def create_farmer_profile_if_farmer(sender, instance, created, **kwargs):
    if created and instance.is_farmer:
        FarmerProfile.objects.create(user=instance)
