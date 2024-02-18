# telegram_integration/models.py

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
