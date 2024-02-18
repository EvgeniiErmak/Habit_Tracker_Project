# telegram_integration/views.py

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from django.contrib.auth.models import User
from users.models import UserProfile  # Импорт модели UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

TELEGRAM_BOT_TOKEN = '6508959358:AAESl7Sb20VbkYx26qU-T0piY0UF_EeiWf8'

# Устанавливаем оптимальный размер пула соединений для Telegram API
import requests
from requests.adapters import HTTPAdapter


class TelegramSession(requests.Session):
    def __init__(self):
        super(TelegramSession, self).__init__()
        self.mount('https://api.telegram.org', HTTPAdapter(pool_connections=8, pool_maxsize=8))


# Инициализируем нашу сессию
requests = TelegramSession()

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция для обновления профиля пользователя
def update_user_profile(user_id, chat_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = User.objects.create(id=user_id)

    user_profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'telegram_chat_id': chat_id}
    )

    if not created:
        user_profile.telegram_chat_id = chat_id
        user_profile.save()

    return user_profile


# Функция для команды /start
def start(update: Update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_profile = update_user_profile(user_id, chat_id)
    context.bot.send_message(chat_id=chat_id,
                             text='Добро пожаловать в Habit Tracker! Вы будете получать напоминания о ваших привычках здесь.')


# Функция для обработки ошибок
def error(update: Update, context):
    logger.warning(f'Обновление {update} вызвало ошибку {context.error}')


# Функция для эхо-ответа
def echo(update: Update, context):
    update.message.reply_text(update.message.text)


# Функция для обработки вебхука
@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        updater = Updater(bot=bot, use_context=True)
        update = Update.de_json(request.body, bot)
        updater.dispatcher.process_update(update)
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# Запуск бота, если файл запущен как скрипт
if __name__ == "__main__":
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    # Добавляем обработчики команд и сообщений
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_error_handler(error)

    # Запускаем обновления
    updater.start_polling()
    updater.idle()
