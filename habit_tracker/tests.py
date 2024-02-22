# habit_tracker/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Habit
from .serializers import HabitSerializer


class HabitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.habit_data = {
            'user': self.user,
            'name': 'Test Habit',
            'place': 'Test Place',
            'time': '12:00',
            'action': 'Test Action',
            'pleasant': True,
            'related_habit': None,
            'frequency': 'каждый день',
            'reward': 'Test Reward',
            'duration': 2,
            'is_public': False,
            'time_to_complete': 'Test Time',
            'publicity': False,
        }
        self.habit = Habit.objects.create(**self.habit_data)
        self.client = APIClient()

    def test_habit_model(self):
        self.assertEqual(str(self.habit), self.habit_data['name'])

    def test_habit_serializer(self):
        serializer = HabitSerializer(instance=self.habit)
        self.assertEqual(serializer.data, self.habit_data)

    def test_habit_view_set(self):
        self.client.force_login(user=self.user)

        # Test Create
        response = self.client.post('/api/habits/', data=self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test List
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Including the one created in the setup

        # Test Retrieve
        response = self.client.get(f'/api/habits/{self.habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test Update
        updated_data = {'name': 'Updated Habit'}
        response = self.client.put(f'/api/habits/{self.habit.id}/', data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])

        # Test Delete
        response = self.client.delete(f'/api/habits/{self.habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)

    def test_public_habit_list_view(self):
        response = self.client.get('/api/habits/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_habit_list_view(self):
        self.client.force_login(user=self.user)
        response = self.client.get('/api/habits/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_habit_create_view(self):
        self.client.force_login(user=self.user)
        response = self.client.post('/api/habits/create/', data=self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_habit_update_view(self):
        self.client.force_login(user=self.user)
        updated_data = {'name': 'Updated Habit'}
        response = self.client.put(f'/api/habits/{self.habit.id}/update/', data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])

    def test_habit_delete_view(self):
        self.client.force_login(user=self.user)
        response = self.client.delete(f'/api/habits/{self.habit.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)
