# telegram_integration/views.py

import os
import django
import logging
from django.http import HttpResponse
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

# Указание пути к файлу с настройками Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализация Django
django.setup()

# Импорт модели UserProfile после инициализации Django
from telegram_integration.models import UserProfile

# Инициализация объекта logger
logger = logging.getLogger(__name__)

# Токен бота Telegram
TELEGRAM_BOT_TOKEN = '6508959358:AAESl7Sb20VbkYx26qU-T0piY0UF_EeiWf8'


def start(update: Update, context):
    user_id = update.effective_user.id
    chat_id = update.message.chat_id
    user_profile, created = UserProfile.objects.get_or_create(
        user_id=user_id,
        defaults={'telegram_chat_id': chat_id}
    )

    if not created:
        # Если профиль уже существует, обновим telegram_chat_id
        user_profile.telegram_chat_id = chat_id
        user_profile.save()

    context.bot.send_message(chat_id=chat_id,
                             text='Welcome to Habit Tracker! You will receive reminders about your habits here.')


# Функция, выполняемая при возникновении ошибки
def error(update: Update, context):
    logger.warning(f'Update {update} caused error {context.error}')


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
    return HttpResponse('ok')


# Запуск бота, если файл запущен как скрипт
if __name__ == "__main__":
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
