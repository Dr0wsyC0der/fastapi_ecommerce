# FastAPI E-commerce API

Подробный `REST API` для интернет-магазина на `FastAPI` с авторизацией по `JWT`, каталогом товаров, категориями, отзывами, корзиной, заказами, загрузкой изображений и миграциями через `Alembic`.

## О проекте

Проект реализует backend-часть небольшого e-commerce приложения. API разделено по ролям пользователей и покрывает типовой сценарий интернет-магазина:

- регистрация и аутентификация пользователей;
- роли `buyer`, `seller`, `admin`;
- управление категориями;
- создание и публикация товаров продавцами;
- загрузка изображений товаров;
- фильтрация, пагинация и полнотекстовый поиск по товарам;
- добавление товаров в корзину;
- оформление заказа на основе корзины;
- отзывы покупателей и пересчёт рейтинга товара;
- миграции базы данных через `Alembic`.

## Основные возможности

### Аутентификация и роли

- регистрация пользователя с ролью `buyer`, `seller` или `admin`;
- вход через `OAuth2PasswordRequestForm`;
- выдача `access_token` и `refresh_token`;
- защита маршрутов по ролям.

### Каталог

- древовидные категории через `parent_id`;
- список активных категорий;
- мягкое удаление категорий через `is_active`.

### Товары

- CRUD для товаров;
- доступ на создание, изменение и удаление только для продавца;
- загрузка изображения товара;
- фильтрация по категории, продавцу, наличию и диапазону цен;
- пагинация;
- полнотекстовый поиск PostgreSQL по `name` и `description`;
- мягкое удаление товаров.

### Корзина и заказы

- получение текущей корзины пользователя;
- добавление, изменение и удаление позиций;
- очистка корзины;
- оформление заказа из корзины;
- сохранение состава заказа и итоговой суммы;
- уменьшение остатков при покупке.

### Отзывы

- отзыв может создать только покупатель;
- удалять отзывы может только администратор;
- рейтинг товара пересчитывается автоматически.

## Стек

- `Python 3.12+`
- `FastAPI`
- `SQLAlchemy 2.0`
- `PostgreSQL`
- `asyncpg`
- `Alembic`
- `Pydantic v2`
- `Uvicorn`
- `PyJWT`
- `Passlib[bcrypt]`

## Структура проекта

```text
fastapi_ecommerce/
|-- app/
|   |-- main.py                 # Точка входа FastAPI
|   |-- auth.py                 # JWT, хеширование паролей, проверки ролей
|   |-- config.py               # Загрузка SECRET_KEY из .env
|   |-- database.py             # SQLAlchemy engine и async session
|   |-- db_depends.py           # Зависимости для работы с БД
|   |-- schemas.py              # Pydantic-схемы
|   |-- models/                 # ORM-модели
|   |-- routers/                # Маршруты API
|   `-- migrations/             # Alembic migrations
|-- media/
|   `-- products/               # Загруженные изображения товаров
|-- requirements.txt
|-- alembic.ini
`-- .env
```

## Модель ролей

| Роль | Возможности |
|---|---|
| `buyer` | смотреть товары, работать с корзиной, оформлять заказы, оставлять отзывы |
| `seller` | создавать, изменять и удалять свои товары |
| `admin` | удалять отзывы |

## Сущности системы

### `User`

- `email`
- `hashed_password`
- `role`
- `is_active`

### `Category`

- `name`
- `parent_id`
- `is_active`

### `Product`

- `name`
- `description`
- `price`
- `stock`
- `image_url`
- `category_id`
- `seller_id`
- `rating`
- `is_active`
- `tsv` для полнотекстового поиска в PostgreSQL

### `Review`

- `user_id`
- `product_id`
- `comment`
- `grade`
- `comment_date`
- `is_active`

### `CartItem`

- `user_id`
- `product_id`
- `quantity`

### `Order`

- `user_id`
- `status`
- `total_amount`
- `created_at`
- `updated_at`

### `OrderItem`

- `order_id`
- `product_id`
- `quantity`
- `unit_price`
- `total_price`

## Установка и запуск

### 1. Подготовить окружение

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Создать `.env`

В проекте используется переменная:

```env
SECRET_KEY=your_super_secret_key
```

### 3. Настроить PostgreSQL

Сейчас строка подключения к базе задана напрямую в двух местах:

- `app/database.py`
- `alembic.ini`

Перед запуском убедитесь, что там указан ваш актуальный `PostgreSQL`-сервер, пользователь, пароль, порт и имя базы.

Пример формата:

```text
postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_db
```

### 4. Применить миграции

```powershell
alembic upgrade head
```

### 5. Запустить приложение

```powershell
uvicorn app.main:app --reload
```

После запуска будут доступны:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- API root: `http://127.0.0.1:8000/`

## Маршруты API

### Пользователи и токены

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `POST` | `/users/` | Регистрация пользователя | публично |
| `POST` | `/users/token` | Получение `access_token` и `refresh_token` | публично |
| `POST` | `/users/refresh-token` | Обновление `access_token` | публично |

### Категории

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `GET` | `/categories/` | Список активных категорий | публично |
| `POST` | `/categories/` | Создание категории | публично |
| `PUT` | `/categories/{category_id}` | Обновление категории | публично |
| `DELETE` | `/categories/{category_id}` | Мягкое удаление категории | публично |

### Товары

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `GET` | `/products/` | Список товаров с пагинацией и фильтрами | публично |
| `GET` | `/products/category/{category_id}` | Товары по категории | публично |
| `GET` | `/products/{product_id}` | Карточка товара | публично |
| `POST` | `/products/` | Создание товара | `seller` |
| `PUT` | `/products/{product_id}` | Обновление своего товара | `seller` |
| `DELETE` | `/products/{product_id}` | Мягкое удаление своего товара | `seller` |
| `GET` | `/products/{product_id}/reviews` | Отзывы о товаре | публично |

### Отзывы

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `GET` | `/reviews/` | Список активных отзывов | публично |
| `POST` | `/reviews/` | Создание отзыва | `buyer` |
| `DELETE` | `/reviews/{review_id}` | Удаление отзыва | `admin` |

### Корзина

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `GET` | `/cart/` | Получить текущую корзину | авторизованный пользователь |
| `POST` | `/cart/items` | Добавить товар в корзину | авторизованный пользователь |
| `PUT` | `/cart/items/{product_id}` | Изменить количество товара | авторизованный пользователь |
| `DELETE` | `/cart/items/{product_id}` | Удалить позицию из корзины | авторизованный пользователь |
| `DELETE` | `/cart/` | Очистить корзину | авторизованный пользователь |

### Заказы

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `POST` | `/orders/checkout` | Оформить заказ из корзины | авторизованный пользователь |
| `GET` | `/orders/` | Получить список своих заказов | авторизованный пользователь |
| `GET` | `/orders/{order_id}` | Получить детали заказа | авторизованный пользователь |

## Фильтрация и поиск товаров

Маршрут `GET /products/` поддерживает:

- `page`
- `page_size`
- `category_id`
- `search`
- `min_price`
- `max_price`
- `in_stock`
- `seller_id`

Пример:

```http
GET /products/?page=1&page_size=10&search=iphone&min_price=10000&max_price=90000&in_stock=true
```

Поле `search` использует полнотекстовый поиск PostgreSQL по `name` и `description`.

## Работа с изображениями

- изображения товаров сохраняются в `media/products/`;
- статические файлы раздаются через `/media`;
- разрешены типы: `jpg`, `png`, `webp`;
- максимальный размер файла: `2 MB`.

## Примеры запросов

### Регистрация покупателя

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@example.com",
    "password": "strongpassword",
    "role": "buyer"
  }'
```

### Регистрация продавца

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "strongpassword",
    "role": "seller"
  }'
```

### Логин

```bash
curl -X POST "http://127.0.0.1:8000/users/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seller@example.com&password=strongpassword"
```

### Обновление access token

```bash
curl -X POST "http://127.0.0.1:8000/users/refresh-token?refresh_token=YOUR_REFRESH_TOKEN"
```

### Создание категории

```bash
curl -X POST "http://127.0.0.1:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smartphones",
    "parent_id": null
  }'
```

### Создание товара продавцом

```bash
curl -X POST "http://127.0.0.1:8000/products/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "name=iPhone 15" \
  -F "description=Flagship smartphone" \
  -F "price=99999.99" \
  -F "stock=15" \
  -F "category_id=1" \
  -F "image=@C:/path/to/image.jpg"
```

### Добавление товара в корзину

```bash
curl -X POST "http://127.0.0.1:8000/cart/items" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Оформление заказа

```bash
curl -X POST "http://127.0.0.1:8000/orders/checkout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Создание отзыва

```bash
curl -X POST "http://127.0.0.1:8000/reviews/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "comment": "Отличный товар",
    "grade": 5
  }'
```

## Миграции

В проекте уже есть миграции для:

- базовой схемы PostgreSQL;
- пользователей;
- отзывов;
- корзины;
- полнотекстового поиска;
- заказов и позиций заказа.

Команды:

```powershell
alembic revision --autogenerate -m "describe changes"
alembic upgrade head
alembic downgrade -1
```

## Полезные замечания по текущей реализации

- `SECRET_KEY` берётся из `.env`.
- Подключение к базе данных сейчас не вынесено в переменные окружения, а задано напрямую в коде и `alembic.ini`.
- Категории в текущей реализации доступны без авторизации.
- Для товаров используется мягкое удаление через `is_active`.
- Для отзывов используется мягкое удаление и автоматический пересчёт среднего рейтинга товара.
- При оформлении заказа корзина очищается, а остатки товара уменьшаются.
- Swagger уже хорошо подходит для ручного тестирования API после запуска.

## Идеи для следующего улучшения

- вынести `DATABASE_URL` в `.env`;
- добавить `Docker` и `docker-compose`;
- закрыть административные маршруты авторизацией;
- добавить тесты `pytest`;
- добавить `CI`;
- реализовать статусы заказа и управление ими;
- добавить избранное, оплату и адреса доставки.

## Автор

README подготовлен под текущую структуру проекта и отражает фактические маршруты, схемы и миграции, которые уже есть в кодовой базе.
