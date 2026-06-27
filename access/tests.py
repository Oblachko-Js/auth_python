import bcrypt
import json
from django.test import TestCase, Client
from access.models import Role, BusinessElement, AccessRule
from users.models import User


class AccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name='admin', description='Admin role')
        self.user_role = Role.objects.create(name='user', description='User role')
        self.element = BusinessElement.objects.create(name='products', description='Товары')

        self.admin = User.objects.create(
            first_name='Admin',
            last_name='Adminov',
            patronymic='',
            email='admin@example.com',
            password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.admin_role,
        )
        self.user = User.objects.create(
            first_name='User',
            last_name='Userov',
            patronymic='',
            email='user@example.com',
            password_hash=bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.user_role,
        )

        AccessRule.objects.create(
            role=self.admin_role,
            element=self.element,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )

    def _login(self, email, password):
        response = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': email, 'password': password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        return response.json()['token']

    def test_admin_can_access_roles(self):
        token = self._login('admin@example.com', 'admin123')
        response = self.client.get('/api/access/roles/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_access_roles(self):
        token = self._login('user@example.com', 'user123')
        response = self.client.get('/api/access/roles/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_assign_role(self):
        new_role = Role.objects.create(name='guest', description='Guest role')
        token = self._login('admin@example.com', 'admin123')
        response = self.client.patch(
            f'/api/access/users/{self.user.id}/assign-role/',
            json.dumps({'role_id': new_role.id}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role_id, new_role.id)
