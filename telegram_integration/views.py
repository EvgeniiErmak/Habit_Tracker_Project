# telegram_integration/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .telegram_bot import TelegramBot


@api_view(['POST'])
def send_telegram_message(request):
    message = request.data.get('message')
    TelegramBot.send_message(message)
    return JsonResponse({'success': True})
