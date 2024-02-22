# habit_tracker/validators.py
from django.core.exceptions import ValidationError


def validate_reward_and_related_habit(value, related_habit):
    if value and related_habit:
        raise ValidationError(
            "Привычка не может иметь и вознаграждение, и связанную привычку одновременно."
        )


def validate_duration(value):
    if value > 120:
        raise ValidationError(
            "Время выполнения привычки не должно превышать 120 секунд."
        )


def validate_related_habit(value, pleasant):
    if value and not pleasant:
        raise ValidationError(
            "Связанную привычку можно указывать только для приятных привычек."
        )


def validate_pleasant_habit(value, reward, related_habit):
    if value and (reward or related_habit):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )


def validate_frequency(value):
    if value < 7:
        raise ValidationError("Привычку нельзя выполнять реже, чем 1 раз в 7 дней.")
