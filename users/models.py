from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=30, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    introduction = models.TextField(blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followings', blank=True)

    def __str__(self):
        return self.nickname or self.username

