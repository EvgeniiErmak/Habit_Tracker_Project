# config/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('Habit_Tracker_Project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-reminders': {
        'task': 'telegram_integration.tasks.send_reminders',
        'schedule': crontab(minute=0, hour=8),  # Adjust the schedule as needed
    },
}
