# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # UserProfile이 존재하는지 확인 후 save() 호출
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            # UserProfile이 없는 경우 새로 생성 (예외 상황 대비)
            UserProfile.objects.create(user=instance)  
