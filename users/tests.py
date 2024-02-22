# users/tests.py
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from users.models import UserProfile


class UsersModelsTests(APITestCase):
    def test_user_profile_str_method(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='password123')
        profile = UserProfile.objects.create(user=user, telegram_chat_id='123456')
        self.assertEqual(str(profile), 'test_user')


class UsersViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_view(self):
        response = self.client.post('/users/register/', {'username': 'test_user', 'email': 'test@example.com', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_register_user_view_invalid_data(self):
        response = self.client.post('/users/register/', {'username': 'test_user', 'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username, email, and password are required.')

    def test_custom_token_obtain_pair_view(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='password123')
        response = self.client.post('/users/login/', {'username': 'test_user', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_custom_authentication_view(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='password123')
        self.client.force_authenticate(user=user)
        response = self.client.get('/users/authenticate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_custom_authentication_view_unauthenticated(self):
        response = self.client.get('/users/authenticate/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_view(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='password123')
        refresh_token = user.profile.token
        self.client.force_authenticate(user=user)
        response = self.client.post('/users/logout/', {'refresh_token': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'User successfully logged out.')

    def test_user_logout_view_invalid_token(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='password123')
        self.client.force_authenticate(user=user)
        response = self.client.post('/users/logout/', {'refresh_token': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
