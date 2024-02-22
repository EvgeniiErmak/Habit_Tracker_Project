# habit_tracker/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from .validators import (
    validate_reward_and_related_habit,
    validate_duration,
    validate_related_habit,
    validate_pleasant_habit,
    validate_frequency,
)


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=255)
    time = models.TimeField(default=None, null=True)  # or default='00:00'
    action = models.CharField(max_length=255)
    pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    frequency = models.CharField(
        max_length=50, default="каждый день", validators=[validate_frequency]
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        validators=[validate_reward_and_related_habit],
    )
    duration = models.IntegerField(
        default=2, validators=[MinValueValidator(1), validate_duration]
    )
    is_public = models.BooleanField(default=False)
    time_to_complete = models.CharField(max_length=255, blank=True, null=True)
    publicity = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def clean(self):
        validate_related_habit(self.related_habit, self.pleasant)
        validate_pleasant_habit(self.pleasant, self.reward, self.related_habit)
