import bcrypt
import json
from django.test import TestCase, Client
from access.models import Role, BusinessElement, AccessRule
from users.models import User
from business.views import MOCK_PRODUCTS


class BusinessPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name='admin', description='Admin role')
        self.user_role = Role.objects.create(name='user', description='User role')
        self.denied_role = Role.objects.create(name='denied', description='No permissions')

        self.products_element = BusinessElement.objects.create(name='products', description='Товары')

        AccessRule.objects.create(
            role=self.admin_role,
            element=self.products_element,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )
        AccessRule.objects.create(
            role=self.user_role,
            element=self.products_element,
            read_permission=True,
            read_all_permission=False,
            create_permission=False,
            update_permission=False,
            update_all_permission=False,
            delete_permission=False,
            delete_all_permission=False,
        )

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
        self.denied_user = User.objects.create(
            first_name='Guest',
            last_name='Guestov',
            patronymic='',
            email='noaccess@example.com',
            password_hash=bcrypt.hashpw('nopass123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=self.denied_role,
        )

    def _login(self, email, password):
        response = self.client.post(
            '/api/auth/login/',
            json.dumps({'email': email, 'password': password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        return response.json()['token']

    def test_admin_can_read_all_products(self):
        token = self._login('admin@example.com', 'admin123')
        response = self.client.get('/api/business/products/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_user_can_read_own_products(self):
        token = self._login('user@example.com', 'user123')
        response = self.client.get('/api/business/products/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        expected_products = [p for p in MOCK_PRODUCTS if p['owner_id'] == self.user.id]
        self.assertEqual(response.json(), expected_products)

    def test_user_without_product_access_is_forbidden(self):
        token = self._login('noaccess@example.com', 'nopass123')
        response = self.client.get('/api/business/products/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_product(self):
        token = self._login('admin@example.com', 'admin123')
        payload = {'name': 'New product', 'price': 100}
        response = self.client.post(
            '/api/business/products/',
            json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('product', response.json())
