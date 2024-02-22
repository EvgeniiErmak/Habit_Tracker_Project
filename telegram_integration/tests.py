# telegram_integration/tests.py
from django.contrib.auth.models import User
from .tasks import send_reminders, send_habit_reminder
from django.utils import timezone
from django.urls import reverse, resolve
from unittest.mock import patch, MagicMock
from telegram_integration.views import webhook
from telegram_integration.telegram_bot import TelegramBot
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase, Client
from .views import start, help_command, habits_command, start_adding_habit
from telegram import Update
from users.models import UserProfile
from habit_tracker.models import Habit
from django.apps import apps


class TestTelegramIntegrationConfig(TestCase):
    def test_telegram_integration_config(self):
        app_config = apps.get_app_config('telegram_integration')
        self.assertEqual(app_config.name, 'telegram_integration')
        self.assertEqual(app_config.verbose_name, 'Telegram Integration')


class TelegramIntegrationViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='test_user')
        self.user_profile = UserProfile.objects.create(user=self.user, telegram_chat_id=12345)

    def test_start_command(self):
        update = Update(message=MockChat(id=12345), effective_user=MockUser(id=12345))
        response = start(update, None)
        self.assertEqual(response, "Bot started!")

    def test_help_command(self):
        update = Update(message=MockChat(id=12345), effective_user=MockUser(id=12345))
        response = help_command(update, None)
        expected_response = "List of available commands:\n/start - Start using the application\n/help - Show list of help commands\n/habits - Show list of habits\n/add_habit - Add a new habit"
        self.assertEqual(response, expected_response)

    def test_habits_command_with_existing_user_profile(self):
        update = Update(message=MockChat(id=12345), effective_user=MockUser(id=12345))
        response = habits_command(update, None)
        expected_response = "Ваши привычки:\n1. Habit 1\n2. Habit 2"
        self.assertEqual(response, expected_response)

    def test_habits_command_without_user_profile(self):
        UserProfile.objects.filter(user=self.user).delete()  # Delete user profile for the test
        update = Update(message=MockChat(id=12345), effective_user=MockUser(id=12345))
        response = habits_command(update, None)
        expected_response = "Ваш профиль не найден. Пожалуйста, начните с команды /start."
        self.assertEqual(response, expected_response)

    def test_start_adding_habit(self):
        update = Update(message=MockChat(id=12345), effective_user=MockUser(id=12345))
        response = start_adding_habit(update, None)
        expected_response = "Привет! Давайте начнем создание новой привычки. Пожалуйста, укажите название привычки."
        self.assertEqual(response, expected_response)

    def test_webhook_post_request(self):
        url = reverse('webhook')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class MockChat:
    def __init__(self, id):
        self.id = id


class MockUser:
    def __init__(self, id):
        self.id = id


class HabitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client = APIClient()

    def test_create_habit(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Habit",
            "place": "Test Place",
            "action": "Test Action",
            "pleasant": False,
            "frequency": "Test Frequency",
            "duration": 2
        }
        response = self.client.post('/habits/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.get().name, 'Test Habit')

    def test_retrieve_habit(self):
        self.client.force_authenticate(user=self.user)
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Test Place', action='Test Action',
                                     pleasant=False, frequency='Test Frequency', duration=2)
        response = self.client.get(f'/habits/{habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Habit')

    def test_update_habit(self):
        self.client.force_authenticate(user=self.user)
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Test Place', action='Test Action',
                                     pleasant=False, frequency='Test Frequency', duration=2)
        data = {'name': 'Updated Habit'}
        response = self.client.patch(f'/habits/{habit.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Habit')

    def test_delete_habit(self):
        self.client.force_authenticate(user=self.user)
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Test Place', action='Test Action',
                                     pleasant=False, frequency='Test Frequency', duration=2)
        response = self.client.delete(f'/habits/{habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)


class TelegramIntegrationUrlsTestCase(TestCase):
    def test_webhook_url_resolves(self):
        url = reverse('webhook')
        self.assertEqual(resolve(url).func, webhook)


class TelegramBotTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bot = TelegramBot('test_token')

    @patch('telegram_integration.telegram_bot.Bot')
    @patch('telegram_integration.telegram_bot.Updater')
    def test_start_bot(self, mock_updater, mock_bot):
        self.bot.start_bot()
        mock_bot.assert_called_once_with('test_token')
        mock_updater.assert_called_once_with(bot=mock_bot.return_value, use_context=True)

    def test_start_handler(self):
        update = Update(12345)
        context = MagicMock()
        self.bot.start_handler(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12345, text="Bot started!")

    def test_help_handler(self):
        update = Update(12345)
        context = MagicMock()
        self.bot.help_handler(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12345, text='List of available commands:\n/start - Start using the application\n/help - Show list of help commands\n/habits - Show list of habits\n/add_habit - Add a new habit')

    def test_habits_handler(self):
        update = Update(12345)
        context = MagicMock()
        self.bot.habits_handler(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12345, text='List of your habits:\n1. Habit 1\n2. Habit 2')

    def test_add_habit_handler(self):
        update = Update(12345)
        context = MagicMock()
        self.bot.add_habit_handler(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12345, text='Enter the name of the new habit')

    def test_echo_handler(self):
        update = Update(12345, message=MagicMock(text="Test Message"))
        context = MagicMock()
        self.bot.echo_handler(update, context)
        context.bot.send_message.assert_called_once_with(chat_id=12345, text='You said: Test Message')

    @patch('telegram_integration.telegram_bot.logger')
    def test_error_handler(self, mock_logger):
        update = MagicMock()
        context = MagicMock(error='Test Error')
        self.bot.error_handler(update, context)
        mock_logger.error.assert_called_once_with(f"Update {update} caused error Test Error")


class TelegramIntegrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='testpassword')

    @patch('telegram_integration.tasks.TelegramBot')
    def test_send_reminders(self, mock_telegram_bot):
        current_time = timezone.now().time()
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Home', time=current_time)
        send_reminders()
        mock_telegram_bot.assert_called_once_with(token='TELEGRAM_BOT_TOKEN')
        mock_telegram_bot.return_value.send_message.assert_called_once_with(chat_id=616388234, text=f"Don't forget to do your habit: {habit.action} at {habit.place}!")

    @patch('telegram_integration.tasks.TelegramBot')
    def test_send_habit_reminder(self, mock_telegram_bot):
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Home', time=timezone.now().time())
        habit_id = habit.id
        send_habit_reminder(habit_id)
        mock_telegram_bot.assert_called_once_with(token='TELEGRAM_BOT_TOKEN')
        mock_telegram_bot.return_value.send_message.assert_called_once_with(chat_id=616388234, text=f"Don't forget to do your habit: {habit.action} at {habit.place}!")

