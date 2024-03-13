# telegram_integration/tasks.py
from habit_tracker.models import Habit
from .telegram_bot import TelegramBot
from django.utils import timezone
from celery import shared_task


@shared_task
def send_reminders():
    current_time = timezone.now().time()
    habits_to_remind = Habit.objects.filter(time=current_time)

    for habit in habits_to_remind:
        send_habit_reminder.delay(habit.id)


@shared_task
def send_habit_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        user_chat_id = habit.user.profile.telegram_chat_id  # Replace with actual field name

        message = f"Don't forget to do your habit: {habit.action} at {habit.place}!"

        bot = TelegramBot(token="TELEGRAM_BOT_TOKEN")
        bot.send_message(chat_id=user_chat_id, text=message)  # Use user_chat_id variable
    except Habit.DoesNotExist:
        pass  # Handle the case when habit is deleted before the reminder is sent
