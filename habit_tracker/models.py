# habit_tracker/models.py
from django.db import models
from django.contrib.auth.models import User


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    place = models.CharField(max_length=255)
    time = models.TimeField()
    frequency = models.PositiveIntegerField(default=1)  # В днях
    is_public = models.BooleanField(default=False)
    reward = models.CharField(max_length=255, blank=True)
    pleasant_habit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class UserHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    last_completed = models.DateTimeField(null=True, blank=True)


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=255)


class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='habit_rewards')
    description = models.CharField(max_length=255)
