# habit_tracker/tests.py
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import TestCase
from .models import Habit


class HabitModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            place='Test Place',
            time=None,
            action='Test Action',
            pleasant=False,
            frequency='каждый день',
            duration=2,
        )

    def test_habit_created_successfully(self):
        self.assertEqual(Habit.objects.count(), 1)
        habit = Habit.objects.first()
        self.assertEqual(habit.name, 'Test Habit')

    def test_habit_related_name(self):
        self.assertEqual(self.user.habits.count(), 1)
        habit = self.user.habits.first()
        self.assertEqual(habit.name, 'Test Habit')


class HabitPermissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='54321')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            place='Test Place',
            time=None,
            action='Test Action',
            pleasant=False,
            frequency='каждый день',
            duration=2,
        )
        self.client = APIClient()

    def test_habit_owner_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/update-habit/{self.habit.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_other_user_permission(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/update-habit/{self.habit.pk}/')
        self.assertEqual(response.status_code, 403)


class HabitViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = APIClient()

    def test_habit_list_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/habits/')
        self.assertEqual(response.status_code, 200)

    def test_public_habit_list_view(self):
        response = self.client.get('/public-habits/')
        self.assertEqual(response.status_code, 200)

    def test_user_habit_list_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/my-habits/')
        self.assertEqual(response.status_code, 200)

    def test_habit_create_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/create-habit/', {'name': 'New Habit', 'place': 'New Place', 'action': 'New Action', 'pleasant': False, 'frequency': 'каждый день', 'duration': 2})
        self.assertEqual(response.status_code, 201)

    def test_habit_update_view(self):
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Test Place', time=None, action='Test Action', pleasant=False, frequency='каждый день', duration=2)
        self.client.force_authenticate(user=self.user)
        response = self.client.put(f'/update-habit/{habit.pk}/', {'name': 'Updated Habit', 'place': 'Updated Place', 'action': 'Updated Action', 'pleasant': False, 'frequency': 'каждый день', 'duration': 2})
        self.assertEqual(response.status_code, 200)

    def test_habit_delete_view(self):
        habit = Habit.objects.create(user=self.user, name='Test Habit', place='Test Place', time=None, action='Test Action', pleasant=False, frequency='каждый день', duration=2)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/delete-habit/{habit.pk}/')
        self.assertEqual(response.status_code, 204)
