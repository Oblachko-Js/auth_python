# Auth System — Django REST Framework

Система аутентификации и авторизации на основе JWT и RBAC.

## Технологии

- Python 3.10+
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL
- bcrypt
- PyJWT

## Быстрый старт

```bash
# При использовании виртуального окружения
source .venv/bin/activate
pip install -r requirements.txt

# Создать файл .env из примера и заполнить значения
cp .env.example .env

# Создать базу данных PostgreSQL
createdb auth_db

# Применить миграции
python manage.py migrate

# Заполнить тестовые данные
python manage.py seed_data

# Запустить сервер
python manage.py runserver
```

## Структура данных

### Таблица `users`
| Поле          | Тип       | Описание                          |
|---------------|-----------|-----------------------------------|
| id            | int PK    |                                   |
| first_name    | varchar   | Имя                               |
| last_name     | varchar   | Фамилия                           |
| patronymic    | varchar   | Отчество                          |
| email         | varchar   | Уникальный, используется для входа |
| password_hash | varchar   | bcrypt-хеш пароля                 |
| role_id       | FK→roles  | Роль пользователя                 |
| is_active     | bool      | False = мягкое удаление           |
| created_at    | timestamp |                                   |
| updated_at    | timestamp |                                   |

### Таблица `roles`
| Поле        | Тип     | Описание                |
|-------------|---------|-------------------------|
| id          | int PK  |                         |
| name        | varchar | admin / manager / user / guest |
| description | text    |                         |

### Таблица `business_elements`
| Поле        | Тип     | Описание                              |
|-------------|---------|---------------------------------------|
| id          | int PK  |                                       |
| name        | varchar | products / orders / shops / users / access_rules |
| description | text    |                                       |

### Таблица `access_rules`
| Поле                  | Тип         | Описание                                      |
|-----------------------|-------------|-----------------------------------------------|
| id                    | int PK      |                                               |
| role_id               | FK→roles    |                                               |
| element_id            | FK→elements |                                               |
| read_permission       | bool        | Читать свои объекты (owner_id = user.id)       |
| read_all_permission   | bool        | Читать все объекты                            |
| create_permission     | bool        | Создавать объекты                             |
| update_permission     | bool        | Редактировать свои объекты                    |
| update_all_permission | bool        | Редактировать все объекты                     |
| delete_permission     | bool        | Удалять свои объекты                          |
| delete_all_permission | bool        | Удалять все объекты                           |

## Права ролей (тестовые данные)

| Роль    | products            | orders              | shops          | users    | access_rules |
|---------|---------------------|---------------------|----------------|----------|--------------|
| admin   | полный доступ       | полный доступ       | полный доступ  | полный   | полный       |
| manager | r_a + c + u + d     | аналогично          | аналогично     | read     | —            |
| user    | CRUD своих          | CRUD своих          | только чтение  | —        | —            |
| guest   | read_all            | read (своих нет)    | read_all       | —        | —            |

## Аутентификация

1. Пользователь входит через `POST /api/auth/login/` и получает JWT-токен.
2. Токен передаётся в заголовке каждого запроса:
   ```http
   Authorization: Bearer <token>
   ```
3. `AuthMiddleware` декодирует токен, находит пользователя и присваивает `request.user`.
4. Если токен отсутствует или неверен, `request.user` остаётся `None`.
5. Защищённые эндпоинты возвращают `401`, если пользователь не авторизован.
6. Если пользователь авторизован, но не имеет нужного права, возвращается `403`.

Logout статeless: клиент удаляет токен на своей стороне.

## API эндпоинты

### Аутентификация
| Метод | URL                    | Описание             |
|-------|------------------------|----------------------|
| POST  | /api/auth/register/    | Регистрация          |
| POST  | /api/auth/login/       | Вход                 |
| POST  | /api/auth/logout/      | Выход                |
| GET   | /api/auth/profile/     | Профиль              |
| PATCH | /api/auth/profile/     | Обновить профиль     |
| DELETE| /api/auth/profile/     | Мягкое удаление      |

### Управление доступом (только admin)
| Метод  | URL                                     | Описание                        |
|--------|-----------------------------------------|---------------------------------|
| GET    | /api/access/roles/                      | Список ролей                    |
| POST   | /api/access/roles/                      | Создать роль                    |
| GET    | /api/access/roles/{id}/                 | Роль по id                      |
| PATCH  | /api/access/roles/{id}/                 | Обновить роль                   |
| DELETE | /api/access/roles/{id}/                 | Удалить роль                    |
| GET    | /api/access/elements/                   | Список бизнес-элементов         |
| POST   | /api/access/elements/                   | Создать бизнес-элемент          |
| GET    | /api/access/rules/                      | Список правил доступа           |
| POST   | /api/access/rules/                      | Создать правило                 |
| GET    | /api/access/rules/{id}/                 | Правило по id                   |
| PATCH  | /api/access/rules/{id}/                 | Изменить правило                |
| DELETE | /api/access/rules/{id}/                 | Удалить правило                 |
| PATCH  | /api/access/users/{user_id}/assign-role/| Назначить роль пользователю     |

### Бизнес-объекты (mock)
| Метод | URL                     | Описание        |
|-------|-------------------------|-----------------|
| GET   | /api/business/products/ | Список товаров  |
| POST  | /api/business/products/ | Создать товар   |
| GET   | /api/business/orders/   | Список заказов  |
| POST  | /api/business/orders/   | Создать заказ   |
| GET   | /api/business/shops/    | Список магазинов |

## Тестирование

В проекте реализованы базовые модульные тесты для следующих приложений:

- `users` — регистрация, вход, профиль, мягкое удаление.
- `access` — проверка админского доступа и назначения ролей.
- `business` — проверка доступа к mock-бизнес-объектам и создание товара.

Запуск тестов:

```bash
source .venv/bin/activate
python manage.py test users access business
```

## Тестовые аккаунты

| Email                 | Пароль     | Роль    |
|-----------------------|------------|---------|
| admin@example.com     | admin123   | admin   |
| manager@example.com   | manager123 | manager |
| user@example.com      | user123    | user    |
| guest@example.com     | guest123   | guest   |

## Примеры запросов

1. Логин

POST http://127.0.0.1:8000/api/auth/login/

json

{
  "email": "admin@example.com",
  "password": "admin123"
}

2. Регистрация

POST http://127.0.0.1:8000/api/auth/register/

json

{
  "first_name": "Тест",
  "last_name": "Тестов",
  "patronymic": "Тестович",
  "email": "test@example.com",
  "password": "test123",
  "password_confirm": "test123"
}

3. Профиль

GET http://127.0.0.1:8000/api/auth/profile/

4. Обновление профиля

PATCH http://127.0.0.1:8000/api/auth/profile/

json

{
  "first_name": "Новоеимя"
}

5. Выход

POST http://127.0.0.1:8000/api/auth/logout/

6. Список товаров

GET http://127.0.0.1:8000/api/business/products/

7. Список заказов

GET http://127.0.0.1:8000/api/business/orders/

8. Список магазинов

GET http://127.0.0.1:8000/api/business/shops/

9. Список правил доступа (только admin)

GET http://127.0.0.1:8000/api/access/rules/

10. Изменить правило доступа (только admin)

PATCH http://127.0.0.1:8000/api/access/rules/1/

json

{
  "create_permission": false
}

11. Назначить роль пользователю (только admin)

PATCH http://127.0.0.1:8000/api/access/users/3/assign-role/

json

{
  "role_id": 1
}
