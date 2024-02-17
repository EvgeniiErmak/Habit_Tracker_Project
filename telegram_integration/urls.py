# telegram_integration/urls.py
from django.urls import path
from .views import send_telegram_message

urlpatterns = [
    path('send-message/', send_telegram_message, name='send_telegram_message'),
]
