# Little Lemon Restaurant API

Back-end capstone project for the Meta Back-End Developer program. A REST API for the
fictional **Little Lemon** restaurant, built with Django and the Django REST Framework,
backed by a MySQL database.

The API exposes CRUD operations for the restaurant menu and a token-secured table
booking service, plus user registration, login and logout via Djoser.

## Tech stack

| Component | Version |
|-----------|---------|
| Python | 3.14 |
| Django | 5.2 (LTS) |
| Django REST Framework | 3.18 |
| Djoser | 2.3 |
| Database | MySQL 8.0 (via `mysqlclient`) |

> Django is pinned to `>=5.2,<6.0` in `requirements.txt`. Django 6.x requires
> MySQL 8.4+, whereas this project targets MySQL 8.0.

## Project structure

```
littlelemon/
├── manage.py
├── requirements.txt
├── littlelemon/            # project package
│   ├── settings.py         # MySQL config, DRF + Djoser setup, DefaultRouter
│   └── urls.py             # admin, restaurant app, booking router, /auth/ routes
└── restaurant/             # application package
    ├── models.py           # Menu, Booking
    ├── serializers.py      # MenuSerializer, BookingSerializer
    ├── views.py            # MenuItemsView, SingleMenuItemView, BookingViewSet
    ├── urls.py             # menu routes + api-token-auth
    ├── admin.py            # Menu and Booking registered
    ├── migrations/
    ├── static/restaurant/  # littlelemon.png
    └── tests/
        ├── test_models.py  # MenuTest
        └── test_views.py   # MenuViewTest
templates/
└── index.html              # static HTML home page served by Django
```

## Data models

**Menu**

| Field | Type |
|-------|------|
| `title` | `CharField(max_length=255)` |
| `price` | `DecimalField(max_digits=10, decimal_places=2)` |
| `inventory` | `IntegerField` |

**Booking**

| Field | Type |
|-------|------|
| `name` | `CharField(max_length=255)` |
| `no_of_guests` | `IntegerField` |
| `booking_date` | `DateTimeField` |

## Setup

### 1. Prerequisites

* Python 3.10+
* A running MySQL 8.0 server
* Create the database:

  ```sql
  CREATE DATABASE LittleLemon;
  ```

### 2. Virtual environment and dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Database credentials

`littlelemon/settings.py` contains the `DATABASES` configuration. Update `USER` and
`PASSWORD` to match your local MySQL server:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'LittleLemon',
        'USER': 'root',
        'PASSWORD': '',        # <- set your MySQL root password
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}
```

### 4. Migrate and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run

```bash
python manage.py runserver
```

The site is now available at `http://127.0.0.1:8000/`.

## Endpoints

### Static content

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/restaurant/` | Static HTML home page (`index.html`) |
| —   | `/admin/` | Django admin site |

### Menu API (open)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/restaurant/menu/` | List all menu items |
| POST | `/restaurant/menu/` | Create a menu item |
| GET | `/restaurant/menu/<id>` | Retrieve a single menu item |
| PUT | `/restaurant/menu/<id>` | Update a menu item |
| DELETE | `/restaurant/menu/<id>` | Delete a menu item |

`MenuItemsView` extends `ListCreateAPIView`; `SingleMenuItemView` extends
`RetrieveUpdateAPIView` and `DestroyAPIView`.

### Table booking API (token authentication required)

`BookingViewSet` extends `viewsets.ModelViewSet` with
`permission_classes = [IsAuthenticated]`, registered on a `DefaultRouter`.

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/restaurant/booking/tables/` | List bookings |
| POST | `/restaurant/booking/tables/` | Create a booking |
| GET | `/restaurant/booking/tables/<id>/` | Retrieve a booking |
| PUT / PATCH | `/restaurant/booking/tables/<id>/` | Update a booking |
| DELETE | `/restaurant/booking/tables/<id>/` | Delete a booking |

Requests must include an `Authorization: Token <token>` header.

### Authentication

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/restaurant/api-token-auth/` | DRF `obtain_auth_token` – returns `{ "token": ... }` |
| POST | `/auth/users/` | Register a new user (Djoser) |
| GET | `/auth/users/` | List / retrieve current user (Djoser) |
| POST | `/auth/token/login/` | Log in – returns `{ "auth_token": ... }` |
| POST | `/auth/token/logout/` | Log out (invalidates the token) |

DRF is configured with `TokenAuthentication` and `SessionAuthentication`.
`DJOSER = {"USER_ID_FIELD": "username"}`.

#### Example

```bash
# obtain a token
curl -X POST http://127.0.0.1:8000/restaurant/api-token-auth/ \
     -d "username=admin&password=yourpassword"

# use it against the secured booking API
curl http://127.0.0.1:8000/restaurant/booking/tables/ \
     -H "Authorization: Token <token>"
```

## Insomnia walkthrough

The endpoints below use this project's actual routes. Note that the **menu API is
open** and only the **booking API requires a token**.

1. **Register a user** — `POST http://127.0.0.1:8000/auth/users/`, body type **JSON**:

   ```json
   { "username": "testuser", "password": "TestPass123!" }
   ```

2. **Obtain a token** — `POST http://127.0.0.1:8000/restaurant/api-token-auth/`,
   body type **Form / JSON** with `username` and `password`. Copy the `token` value
   from the response.

3. **View menu items** — `GET http://127.0.0.1:8000/restaurant/menu/` (no auth
   needed). Use `GET /restaurant/menu/<id>` for a single item.

4. **Mutate the menu** — send `POST` / `PUT` / `DELETE` to `/restaurant/menu/`
   (or `/restaurant/menu/<id>`) with a JSON body. The menu API is unauthenticated,
   so no header is required.

5. **Book a table (protected)** — in the request's **Auth** tab (or a manual
   header) add `Authorization: Token <token>`, then:
   * `GET  /restaurant/booking/tables/` — list bookings
   * `POST /restaurant/booking/tables/` with
     `{ "name": "Test", "no_of_guests": 4, "booking_date": "2026-09-10T18:30:00Z" }`
   * `PUT` / `PATCH` / `DELETE` `/restaurant/booking/tables/<id>/`

6. **Confirm the guard** — repeat step 5 **without** the `Authorization` header.
   The booking endpoints must return `401 Unauthorized`.

7. **Log out** — `POST http://127.0.0.1:8000/auth/token/logout/` with the
   `Authorization: Token <token>` header to invalidate the token.

> In Insomnia's Auth tab, choose **"API Key"** and set the header name to
> `Authorization` with value `Token <token>`. Do **not** use the "Bearer" option —
> DRF's `TokenAuthentication` expects the `Token` prefix, not `Bearer`.

## Running the tests

```bash
python manage.py test
```

The MySQL user needs the privilege to create a test database
(`test_LittleLemon`). Tests cover:

* `MenuTest.test_get_item` – the `Menu.__str__` representation
* `MenuViewTest.test_getall` – the menu list endpoint against `MenuSerializer` output

## Notes

* `requirements.txt` is a full `pip freeze` of the working environment.
* The virtual environment, `__pycache__/` and any SQLite file are excluded via
  `.gitignore`.
