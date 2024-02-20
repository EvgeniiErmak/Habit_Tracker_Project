# telegram_integration/views.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
from django.contrib.auth.models import User
from users.models import UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from habit_tracker.models import Habit

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

# Список параметров привычки
habit_params = ["место", "время", "действие", "признак приятной привычки", "связанная привычка",
                "периодичность", "вознаграждение", "время на выполнение", "признак публичности"]

# Пример формата ввода данных
example_format = "Пример формата ввода данных:\n" \
                 "Место: Кухня\n" \
                 "Время: Утром\n" \
                 "Действие: Завтрак\n" \
                 "Признак приятной привычки: Да\n" \
                 "Связанная привычка: Пить стакан воды перед едой\n" \
                 "Периодичность: Ежедневно\n" \
                 "Вознаграждение: Посмотреть любимый сериал\n" \
                 "Время на выполнение: 30 минут\n" \
                 "Признак публичности: Нет\n\n" \
                 "Введите значение для параметра '{}':"


# Функция для задания вопросов и создания привычки
def add_habit(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    habit_data = {}

    # Функция для задания вопроса
    def ask_question(param_index):
        if param_index < len(habit_params):
            param_name = habit_params[param_index]
            context.bot.send_message(chat_id=chat_id, text=example_format.format(param_name))
            context.user_data["habit_param_index"] = param_index
        else:
            context.bot.send_message(chat_id=chat_id, text="Привычка успешно создана: {}".format(habit_data))
            # Здесь можно сохранить привычку в базу данных или выполнять другие действия
            context.user_data.pop("habit_param_index")

    # Функция для обработки ответа пользователя
    def handle_answer(update: Update, context: CallbackContext):
        param_index = context.user_data.get("habit_param_index")
        if param_index is not None and 0 <= param_index < len(habit_params):
            param_name = habit_params[param_index]
            habit_data[param_name] = update.message.text
            ask_question(param_index + 1)

    ask_question(0)


# Функция для разбора команды /add_habit и извлечения данных о привычке
def parse_habit_command(message):
    habit_data = {}
    parts = message.split()

    # Проверяем, что команда корректно указана и состоит из двух частей
    if len(parts) != 2 or parts[0] != "/add_habit":
        return None  # Возвращаем None, если команда не соответствует ожидаемому формату

    # Проходимся по каждой части и ищем ключевые слова, чтобы извлечь параметры привычки
    for i in range(len(parts)):
        part = parts[i].lower()

        if part == "место:" and i < len(parts) - 1:
            habit_data["place"] = parts[i + 1]
        elif part == "время:" and i < len(parts) - 1:
            habit_data["time"] = parts[i + 1]
        elif part == "действие:" and i < len(parts) - 1:
            habit_data["action"] = parts[i + 1]
        elif part == "признак" and i < len(parts) - 2 and parts[i + 1] == "приятной" and parts[i + 2] == "привычки:":
            habit_data["pleasant"] = True
        elif part == "связанная" and i < len(parts) - 2 and parts[i + 1] == "привычка:":
            habit_data["related_habit"] = parts[i + 2]
        elif part == "периодичность:" and i < len(parts) - 1:
            habit_data["frequency"] = parts[i + 1]
        elif part == "вознаграждение:" and i < len(parts) - 1:
            habit_data["reward"] = parts[i + 1]
        elif part == "время" and i < len(parts) - 2 and parts[i + 1] == "на" and parts[i + 2] == "выполнение:":
            if i + 3 < len(parts):
                habit_data["time_to_complete"] = parts[i + 3]
        elif part == "признак" and i < len(parts) - 2 and parts[i + 1] == "публичности:":
            habit_data["is_public"] = True if parts[i + 2].lower() == "да" else False

    return habit_data


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
    dp.add_handler(CommandHandler("add_habit", add_habit))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()
