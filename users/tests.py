import bcrypt
import json
from django.test import TestCase, Client
from access.models import Role
from users.models import User


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_role = Role.objects.create(name='user', description='User role')
        self.admin_role = Role.objects.create(name='admin', description='Admin role')

        self.admin = User.objects.create(
            first_name='Admin',
            last_name='Adminov',
            patronymic='',
            email='admin@example.com',
            password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.admin_role,
        )

    def test_register_creates_user(self):
        payload = {
            'first_name': 'Test',
            'last_name': 'Tester',
            'patronymic': 'Testovich',
            'email': 'test@example.com',
            'password': 'test123',
            'password_confirm': 'test123',
        }
        response = self.client.post('/api/auth/register/', json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['user']['role_name'], 'user')

    def test_login_returns_token(self):
        user = User.objects.create(
            first_name='User',
            last_name='Userov',
            patronymic='',
            email='user@example.com',
            password_hash=bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.user_role,
        )
        response = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': 'user@example.com', 'password': 'user123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_profile_requires_auth(self):
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, 401)

    def test_profile_returns_current_user(self):
        response = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': 'admin@example.com', 'password': 'admin123'}),
            content_type='application/json',
        )
        token = response.json()['token']
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        profile_response = self.client.get('/api/auth/profile/', **auth_headers)
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.json()['email'], 'admin@example.com')

    def test_soft_delete_deactivates_user(self):
        user = User.objects.create(
            first_name='User',
            last_name='Userov',
            patronymic='',
            email='user2@example.com',
            password_hash=bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.user_role,
        )
        response = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': 'user2@example.com', 'password': 'user123'}),
            content_type='application/json',
        )
        token = response.json()['token']
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        delete_response = self.client.delete('/api/auth/profile/', **auth_headers)
        self.assertEqual(delete_response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        login_after_delete = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': 'user2@example.com', 'password': 'user123'}),
            content_type='application/json',
        )
        self.assertEqual(login_after_delete.status_code, 401)
