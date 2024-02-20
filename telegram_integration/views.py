# telegram_integration/views.py
import os
import django
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, ConversationHandler, CallbackContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from habit_tracker.models import Habit
from django.http import HttpResponse
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
import logging
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
    user_id = update.effective_user.id

    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        habits = Habit.objects.filter(user=user_profile.user)

        if habits:
            habits_list = "\n".join([f"{index}. {habit.name}" for index, habit in enumerate(habits, start=1)])
            message = f"Ваши привычки:\n{habits_list}"
        else:
            message = "У вас пока нет привычек."
    except UserProfile.DoesNotExist:
        message = "Ваш профиль не найден. Пожалуйста, начните с команды /start."

    context.bot.send_message(chat_id=chat_id, text=message)


# Определяем константы для состояний диалога создания привычки
PLACE, TIME, ACTION, PLEASANT, RELATED_HABIT, FREQUENCY, REWARD, TIME_TO_COMPLETE, PUBLICITY, END = range(10)


# Функция для начала создания привычки
def start_adding_habit(update: Update, context: CallbackContext):
    context.user_data['habit_data'] = {}
    update.message.reply_text("Привет! Давайте начнем создание новой привычки. Пожалуйста, укажите место, где вы будете выполнять эту привычку.")
    return PLACE


# Функция для обработки места
def handle_place(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['place'] = update.message.text
    update.message.reply_text("Отлично! Теперь укажите время, когда вы будете выполнять эту привычку.")
    return TIME


# Добавляем функцию для настройки вебхука
@csrf_exempt
def webhook(request):
    # Проверяем, что запрос пришел методом POST
    if request.method == 'POST':
        # Принимаем обновление от Telegram
        update = Update.de_json(request.body, TELEGRAM_BOT_TOKEN)
        # Обработка обновления
        # ... (ваш код обработки обновления)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)


# Функция для обработки времени
def handle_time(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['time'] = update.message.text
    update.message.reply_text("Хорошо! Теперь укажите действие, которое будет представлять из себя привычка.")
    return ACTION


# Функция для обработки действия
def handle_action(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['action'] = update.message.text
    update.message.reply_text("Отлично! Эта привычка приносит вам удовольствие? (Да/Нет)")
    return PLEASANT


# Функция для обработки признака приятной привычки
def handle_pleasant(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    response = update.message.text.lower()
    if response == 'да':
        habit_data['pleasant'] = True
    elif response == 'нет':
        habit_data['pleasant'] = False
    else:
        update.message.reply_text("Пожалуйста, ответьте 'Да' или 'Нет'.")
        return PLEASANT

    update.message.reply_text("Есть ли у этой привычки связанная привычка? Если есть, укажите ее.")
    return RELATED_HABIT


# Функция для обработки связанной привычки
def handle_related_habit(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['related_habit'] = update.message.text
    update.message.reply_text("Как часто вы будете выполнять эту привычку? (Например, 'ежедневно', 'еженедельно')")
    return FREQUENCY


# Функция для обработки периодичности
def handle_frequency(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['frequency'] = update.message.text
    update.message.reply_text("Какое вознаграждение вы предусматриваете за выполнение этой привычки?")
    return REWARD


# Функция для обработки вознаграждения
def handle_reward(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['reward'] = update.message.text
    update.message.reply_text("Сколько времени вы планируете уделять на выполнение этой привычки? (Например, '30 минут')")
    return TIME_TO_COMPLETE


# Функция для обработки времени на выполнение
def handle_time_to_complete(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    habit_data['time_to_complete'] = update.message.text
    update.message.reply_text("Желаете ли вы делиться этой привычкой публично? (Да/Нет)")
    return PUBLICITY


# Функция для обработки признака публичности
def handle_publicity(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']
    response = update.message.text.lower()
    if response == 'да':
        habit_data['is_public'] = True
    elif response == 'нет':
        habit_data['is_public'] = False
    else:
        update.message.reply_text("Пожалуйста, ответьте 'Да' или 'Нет'.")
        return PUBLICITY

    # Показываем пользователю введенные данные и предлагаем подтвердить создание привычки
    update.message.reply_text(f"Вот информация о вашей привычке:\n{habit_data}\n\n"
                              "Если все верно, нажмите /end, чтобы завершить создание привычки, "
                              "или продолжайте вводить информацию.")

    return END


# Функция для завершения создания привычки
def end_adding_habit(update: Update, context: CallbackContext):
    habit_data = context.user_data['habit_data']

    # Получаем пользователя из базы данных
    user_id = update.effective_user.id
    user, created = User.objects.get_or_create(id=user_id)

    # Создаем новый объект привычки и сохраняем его в базе данных
    habit = Habit.objects.create(
        user=user,
        name=habit_data.get('name', ''),
        place=habit_data.get('place', ''),
        time=habit_data.get('time', ''),
        action=habit_data.get('action', ''),
        pleasant=habit_data.get('pleasant', ''),
        related_habit=habit_data.get('related_habit', ''),
        frequency=habit_data.get('frequency', ''),
        reward=habit_data.get('reward', ''),
        time_to_complete=habit_data.get('time_to_complete', ''),
        publicity=habit_data.get('publicity', ''),
    )

    # Сообщаем пользователю об успешном создании привычки
    update.message.reply_text(f"Привычка успешно создана: {habit_data}")

    # Очищаем данные пользователя
    context.user_data.clear()

    return ConversationHandler.END


# Функция для отмены создания привычки
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Создание привычки отменено.")
    context.user_data.clear()
    return ConversationHandler.END


# Добавляем ConversationHandler для управления диалогом создания привычки
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_habit', start_adding_habit)],
    states={
        PLACE: [MessageHandler(Filters.text & ~Filters.command, handle_place)],
        TIME: [MessageHandler(Filters.text & ~Filters.command, handle_time)],
        ACTION: [MessageHandler(Filters.text & ~Filters.command, handle_action)],
        PLEASANT: [MessageHandler(Filters.text & ~Filters.command, handle_pleasant)],
        RELATED_HABIT: [MessageHandler(Filters.text & ~Filters.command, handle_related_habit)],
        FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, handle_frequency)],
        REWARD: [MessageHandler(Filters.text & ~Filters.command, handle_reward)],
        TIME_TO_COMPLETE: [MessageHandler(Filters.text & ~Filters.command, handle_time_to_complete)],
        PUBLICITY: [MessageHandler(Filters.text & ~Filters.command, handle_publicity)],
        END: [CommandHandler('end', end_adding_habit)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Создаем объект updater и регистрируем обработчиков в нем
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("habits", habits_command))
dp.add_handler(conv_handler)

# Запускаем бота
updater.start_polling()
updater.idle()
