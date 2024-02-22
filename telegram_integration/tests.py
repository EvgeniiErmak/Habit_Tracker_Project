# telegram_integration/tests.py

from telegram_integration.tasks import send_habit_reminder, send_reminders
from django.test import TestCase, Client
from django.contrib.auth.models import User
from telegram_integration.views import update_user_profile
from users.models import UserProfile
from habit_tracker.models import Habit
from telegram_integration.telegram_bot import TelegramBot
from unittest.mock import patch, MagicMock
from telegram import Update
from django.urls import reverse
import json


class TelegramIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, telegram_chat_id='test_chat_id')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            place='Test Place',
            time='12:00',
            action='Test Action',
            pleasant=True,
            related_habit=None,
            frequency='каждый день',
            reward='Test Reward',
            duration=2,
            is_public=False,
            time_to_complete='Test Time',
            publicity=False,
        )
        self.telegram_bot = TelegramBot('test_token')

    def test_update_user_profile(self):
        user_id = 123
        chat_id = 'test_chat_id'
        user_profile = update_user_profile(user_id, chat_id)
        self.assertEqual(user_profile.user.id, user_id)
        self.assertEqual(user_profile.telegram_chat_id, chat_id)

    def test_start_command(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/start'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Добро пожаловать в Habit Tracker!', response.json()['message']['text'])

    def test_help_command(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/help'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Список доступных команд:', response.json()['message']['text'])

    def test_habits_command_with_habits(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/habits'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ваши привычки:', response.json()['message']['text'])

    def test_habits_command_without_habits(self):
        # Remove the habit for this test
        self.habit.delete()
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/habits'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('У вас пока нет привычек.', response.json()['message']['text'])

    def test_add_habit_command(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/add_habit'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Привет! Давайте начнем создание новой привычки.', response.json()['message']['text'])

    def test_stop_bot_command(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/stop_bot'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bot is stopping...', response.json()['message']['text'])
        self.assertIn('Bot stopped successfully.', response.json()['message']['text'])

    def test_handle_name(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Name'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Отлично! Теперь укажите место, где вы будете выполнять эту привычку.', response.json()['message']['text'])

    def test_handle_place(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Place'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Отлично! Теперь укажите время, когда вы будете выполнять эту привычку.', response.json()['message']['text'])

    def test_handle_time(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Time'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Хорошо! Теперь укажите действие, которое будет представлять из себя привычка.', response.json()['message']['text'])

    def test_handle_action(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Action'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Отлично! Эта привычка приносит вам удовольствие? (Да/Нет)', response.json()['message']['text'])

    def test_handle_pleasant(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Да'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Есть ли у этой привычки связанная привычка? Если есть, укажите ее.', response.json()['message']['text'])

    def test_handle_related_habit(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Related Habit'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Как часто вы будете выполнять эту привычку? (Например, \'ежедневно\', \'еженедельно\')', response.json()['message']['text'])

    def test_handle_frequency(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'каждый день'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Какое вознаграждение вы предусматриваете за выполнение этой привычки?', response.json()['message']['text'])

    def test_handle_reward(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Reward'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Сколько времени вы планируете уделять на выполнение этой привычки? (Например, \'30 минут\')', response.json()['message']['text'])

    def test_handle_time_to_complete(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Test Time to Complete'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Желаете ли вы делиться этой привычкой публично? (Да/Нет)', response.json()['message']['text'])

    def test_handle_publicity(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': 'Да'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вот информация о вашей привычке:', response.json()['message']['text'])

    def test_end_adding_habit(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/end'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Привычка успешно создана:', response.json()['message']['text'])

    def test_cancel(self):
        response = self.client.post(reverse('telegram_integration:webhook'), data=json.dumps({'message': {'text': '/cancel'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Создание привычки отменено.', response.json()['message']['text'])

    def test_webhook_view_post(self):
        response = self.client.post(reverse('telegram_integration:webhook'))
        self.assertEqual(response.status_code, 405)

    def test_webhook_view_get(self):
        response = self.client.get(reverse('telegram_integration:webhook'))
        self.assertEqual(response.status_code, 405)


class TelegramBotTests(TestCase):
    def test_send_message(self):
        bot_token = 'test_token'
        chat_id = 'test_chat_id'
        bot = TelegramBot(bot_token)
        message = 'Test message'
        with self.assertRaises(Exception):
            bot.send_message(chat_id, message)  # Not testing actual Telegram API call

    def test_start_handler(self):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = self.create_mock_update()
        context = self.create_mock_context()
        bot.start_handler(update, context)  # Not testing actual Telegram API call

    def test_help_handler(self):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = self.create_mock_update()
        context = self.create_mock_context()
        bot.help_handler(update, context)  # Not testing actual Telegram API call

    def test_habits_handler(self):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = self.create_mock_update()
        context = self.create_mock_context()
        bot.habits_handler(update, context)  # Not testing actual Telegram API call

    def test_add_habit_handler(self):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = self.create_mock_update()
        context = self.create_mock_context()
        bot.add_habit_handler(update, context)  # Not testing actual Telegram API call

    def create_mock_update(self):
        return None  # Return mock update object

    def create_mock_context(self):
        return None  # Return mock context object


class TasksTests(TestCase):
    def setUp(self):
        self.habit = Habit.objects.create(
            name='Test Habit',
            place='Test Place',
            time='12:00',
            action='Test Action',
            pleasant=True,
            related_habit=None,
            frequency='каждый день',
            reward='Test Reward',
            duration=2,
            is_public=False,
            time_to_complete='Test Time',
            publicity=False,
        )

    def test_send_reminders(self):
        send_reminders()  # Not testing actual Celery task execution

    def test_send_habit_reminder(self):
        send_habit_reminder(self.habit.id)  # Not testing actual Celery task execution


class TelegramBotTests(TestCase):
    @patch('telegram_integration.telegram_bot.TelegramBot.send_message')
    def test_start_handler(self, mock_send_message):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = Update(message=MagicMock(text=''))
        context = MagicMock()
        bot.start_handler(update, context)
        mock_send_message.assert_called_once_with(update.effective_chat.id, 'Bot started!')

    @patch('telegram_integration.telegram_bot.TelegramBot.send_message')
    def test_help_handler(self, mock_send_message):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = Update(message=MagicMock(text=''))
        context = MagicMock()
        bot.help_handler(update, context)
        expected_message = 'List of available commands:\n/start - Start using the application\n/help - Show list of help commands\n/habits - Show list of habits\n/add_habit - Add a new habit'
        mock_send_message.assert_called_once_with(update.effective_chat.id, expected_message)

    @patch('telegram_integration.telegram_bot.TelegramBot.send_message')
    def test_habits_handler(self, mock_send_message):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = Update(message=MagicMock(text=''))
        context = MagicMock()
        bot.habits_handler(update, context)
        expected_message = 'List of your habits:\n1. Habit 1\n2. Habit 2'
        mock_send_message.assert_called_once_with(update.effective_chat.id, expected_message)

    @patch('telegram_integration.telegram_bot.TelegramBot.send_message')
    def test_add_habit_handler(self, mock_send_message):
        bot_token = 'test_token'
        bot = TelegramBot(bot_token)
        update = Update(message=MagicMock(text=''))
        context = MagicMock()
        bot.add_habit_handler(update, context)
        mock_send_message.assert_called_once_with(update.effective_chat.id, 'Enter the name of the new habit')


class TasksTests(TestCase):
    @patch('telegram_integration.tasks.TelegramBot')
    @patch('telegram_integration.tasks.Habit')
    def test_send_habit_reminder(self, mock_habit, mock_telegram_bot):
        habit_id = 1
        send_habit_reminder(habit_id)
        mock_habit.objects.get.assert_called_once_with(id=habit_id)
        mock_telegram_bot.assert_called_once_with(token='TELEGRAM_BOT_TOKEN')
        mock_telegram_bot.return_value.send_message.assert_called_once_with(616388234, 'Don\'t forget to do your habit: Test Action at Test Place!')
