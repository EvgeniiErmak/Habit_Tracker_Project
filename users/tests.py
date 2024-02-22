# users/tests.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse, resolve
from users.views import RegisterUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.test import SimpleTestCase
from django.test import TestCase
from users.models import UserProfile


class UserProfileModelTestCase(TestCase):
    def test_user_profile_creation(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        profile = UserProfile.objects.create(user=user, telegram_chat_id='12345')
        self.assertEqual(profile.user.username, 'test_user')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.telegram_chat_id, '12345')


class UsersUrlsTestCase(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterUserView)

    def test_token_obtain_pair_url_resolves(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(resolve(url).func.view_class, CustomTokenObtainPairView)

    def test_token_refresh_url_resolves(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)


class UsersViewsTestCase(APITestCase):
    def test_register_user_view(self):
        url = '/users/register/'
        data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'test_password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_custom_token_obtain_pair_view(self):
        User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        url = '/users/login/'
        data = {'username': 'test_user', 'password': 'test_password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

    def test_custom_authentication_view(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        url = '/users/auth/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_user_logout_view(self):
        user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        refresh = RefreshToken.for_user(user)
        url = '/users/logout/'
        data = {'refresh_token': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'User successfully logged out.')

