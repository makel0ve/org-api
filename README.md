# Org API

REST API для управления организационной структурой компании: иерархия подразделений и сотрудники.

## Стек

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **Gunicorn + Uvicorn** — сервер
- **Docker + docker-compose** — контейнеризация

## Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/makel0ve/org-api.git
cd org-api
```

### 2. Создать `.env` из примера

```bash
cp .env.example .env
```

### 3. Запустить контейнеры

```bash
docker-compose up --build -d
```

### 4. Применить миграции

```bash
docker exec -it org_api_app alembic upgrade head
```

Приложение доступно на `http://localhost:8000`.

## Документация

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тесты

```bash
pip install -r requirements.txt
pytest
```

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/v1/departments/` | Создать подразделение |
| GET | `/api/v1/departments/{id}` | Получить подразделение с деревом |
| PATCH | `/api/v1/departments/{id}` | Обновить подразделение |
| DELETE | `/api/v1/departments/{id}` | Удалить подразделение |
| POST | `/api/v1/departments/{id}/employees/` | Создать сотрудника |

## Структура проекта

```
app/
├── api/        # роутеры
├── core/       # конфиг, база, логгирование
├── models/     # ORM-модели
├── repositories/ # работа с БД
├── schemas/    # Pydantic-схемы
└── services/   # бизнес-логика
```