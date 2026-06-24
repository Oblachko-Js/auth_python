"""
python manage.py seed_data
Заполняет БД начальными данными: роли, бизнес-элементы, правила доступа, тестовые пользователи.
"""
import bcrypt
from django.core.management.base import BaseCommand
from access.models import Role, BusinessElement, AccessRule
from users.models import User


ROLES = [
    ('admin', 'Полный доступ ко всем ресурсам'),
    ('manager', 'Управление товарами, заказами и магазинами'),
    ('user', 'Доступ к собственным объектам'),
    ('guest', 'Только чтение публичных объектов'),
]

ELEMENTS = [
    ('products', 'Товары'),
    ('orders', 'Заказы'),
    ('shops', 'Магазины'),
    ('users', 'Пользователи'),
    ('access_rules', 'Правила доступа'),
]

RULES = [
    ('admin', 'products',     True, True, True, True, True, True, True),
    ('admin', 'orders',       True, True, True, True, True, True, True),
    ('admin', 'shops',        True, True, True, True, True, True, True),
    ('admin', 'users',        True, True, True, True, True, True, True),
    ('admin', 'access_rules', True, True, True, True, True, True, True),
    ('manager', 'products', True, True,  True, True, False, True, False),
    ('manager', 'orders',   True, True,  True, True, False, True, False),
    ('manager', 'shops',    True, False, True, True, False, True, False),
    ('manager', 'users',    True, False, False, False, False, False, False),
    ('user', 'products', True, False, True, True, False, True, False),
    ('user', 'orders',   True, False, True, True, False, True, False),
    ('user', 'shops',    True, False, False, False, False, False, False),
    ('guest', 'products', True, True,  False, False, False, False, False),
    ('guest', 'orders',   True, False, False, False, False, False, False),
    ('guest', 'shops',    True, True,  False, False, False, False, False),
]

USERS = [
    ('Иван',   'Иванов',  'Иванович',  'admin@example.com',   'admin123',   'admin'),
    ('Мария',  'Петрова', 'Сергеевна', 'manager@example.com', 'manager123', 'manager'),
    ('Алексей','Сидоров', 'Петрович',  'user@example.com',    'user123',    'user'),
    ('Гость',  'Гостев',  '',          'guest@example.com',   'guest123',   'guest'),
]


class Command(BaseCommand):
    help = 'Заполнить БД тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Создание ролей...')
        role_map = {}
        for name, desc in ROLES:
            role, _ = Role.objects.get_or_create(name=name, defaults={'description': desc})
            role_map[name] = role

        self.stdout.write('Создание бизнес-элементов...')
        element_map = {}
        for name, desc in ELEMENTS:
            el, _ = BusinessElement.objects.get_or_create(name=name, defaults={'description': desc})
            element_map[name] = el

        self.stdout.write('Создание правил доступа...')
        for role_name, el_name, read, read_all, create, upd, upd_all, dlt, dlt_all in RULES:
            rule, created = AccessRule.objects.get_or_create(
                role=role_map[role_name],
                element=element_map[el_name],
                defaults={
                    'read_permission': read, 'read_all_permission': read_all,
                    'create_permission': create, 'update_permission': upd,
                    'update_all_permission': upd_all, 'delete_permission': dlt,
                    'delete_all_permission': dlt_all,
                }
            )
            if not created:
                rule.read_permission = read; rule.read_all_permission = read_all
                rule.create_permission = create; rule.update_permission = upd
                rule.update_all_permission = upd_all; rule.delete_permission = dlt
                rule.delete_all_permission = dlt_all; rule.save()

        self.stdout.write('Создание тестовых пользователей...')
        for first, last, pat, email, password, role_name in USERS:
            if not User.objects.filter(email=email).exists():
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                User.objects.create(
                    first_name=first, last_name=last, patronymic=pat,
                    email=email, password_hash=hashed, role=role_map[role_name],
                )
                self.stdout.write(f'  + {email} ({role_name})')
            else:
                self.stdout.write(f'  ~ {email} уже существует')

        self.stdout.write(self.style.SUCCESS('Готово!'))
