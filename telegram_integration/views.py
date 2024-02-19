# telegram_integration/views.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from django.contrib.auth.models import User
from users.models import UserProfile
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
    menu_text = "Добро пожаловать в Habit Tracker! Вы будете получать напоминания о ваших привычках здесь.\n" \
                "Вот список доступных команд:\n" \
                "/start - Начать использование приложения\n" \
                "/help - Показать список команд помощи\n" \
                "/habits - Показать список привычек\n" \
                "/add_habit - Добавить новую привычку"
    context.bot.send_message(chat_id=chat_id, text=menu_text)


# Функция для команды /help
def help_command(update: Update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id,
                             text='Список доступных команд:\n'
                                  '/start - Начать использование приложения\n'
                                  '/help - Показать список команд помощи\n'
                                  '/habits - Показать список привычек\n'
                                  '/add_habit - Добавить новую привычку')


# Функция для команды /habits
def habits_command(update: Update, context):
    chat_id = update.effective_chat.id
    # Здесь добавьте логику для отображения списка привычек пользователю
    context.bot.send_message(chat_id=chat_id, text='Список ваших привычек:\n1. Привычка 1\n2. Привычка 2')


# Функция для команды /add_habit
def add_habit_command(update: Update, context):
    chat_id = update.effective_chat.id
    # Здесь добавьте логику для добавления новой привычки пользователю
    context.bot.send_message(chat_id=chat_id, text='Введите название новой привычки')


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

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("habits", habits_command))
    dp.add_handler(CommandHandler("add_habit", add_habit_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()
