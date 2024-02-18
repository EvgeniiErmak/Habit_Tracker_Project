# telegram_integration/views.py

import os
import sys

import django
import logging
from django.http import HttpResponse
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

# Установка оптимального размера пула соединений для Telegram API
import requests
from requests.adapters import HTTPAdapter

TELEGRAM_BOT_TOKEN = '6508959358:AAESl7Sb20VbkYx26qU-T0piY0UF_EeiWf8'


class TelegramSession(requests.Session):
    def __init__(self):
        super(TelegramSession, self).__init__()
        self.mount('https://api.telegram.org', HTTPAdapter(pool_connections=8, pool_maxsize=8))


requests = TelegramSession()

# Указание пути к файлу с настройками Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализация Django
django.setup()

# Импорт модели UserProfile после инициализации Django
from users.models import UserProfile

# Инициализация объекта logger
logger = logging.getLogger(__name__)


# Определение функции для обновления профиля пользователя
def update_user_profile(user_id, chat_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        # Если профиль уже существует, обновим telegram_chat_id
        user_profile.telegram_chat_id = chat_id
        user_profile.save()
    except UserProfile.DoesNotExist:
        # Если профиля нет, создадим новый
        user_profile = UserProfile.objects.create(user_id=user_id, telegram_chat_id=chat_id)

    return user_profile


# Определение функции для команды /start
def start(update: Update, context):
    user_id = update.effective_user.id  # Получаем идентификатор пользователя
    chat_id = update.effective_chat.id  # Получаем идентификатор чата

    user_profile = update_user_profile(user_id, chat_id)

    context.bot.send_message(chat_id=chat_id,
        text='Добро пожаловать в Habit Tracker! Вы будете получать напоминания о ваших привычках здесь.')


# Функция, выполняемая при возникновении ошибки
def error(update: Update, context):
    logger.warning(f'Обновление {update} вызвало ошибку {context.error}')


# Функция для эхо-ответа
def echo(update: Update, context):
    update.message.reply_text(update.message.text)


# Функция для обработки вебхука
def webhook(request):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(bot=bot, use_context=True)
    if request.method == 'POST':
        update = Update.de_json(request.body, bot)
        updater.dispatcher.process_update(update)
    return HttpResponse('ок')


# Запуск бота, если файл запущен как скрипт
if __name__ == "__main__":
    # Добавляем эту строку для правильной инициализации Django
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    # Добавление обработчиков команд и сообщений
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Обработка ошибок
    dp.add_error_handler(error)

    # Запуск обновлений
    updater.start_polling()
    updater.idle()
