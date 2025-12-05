# Архитектура системы

## Общее описание

Система состоит из трёх основных компонентов:

1. **Backend (Python/Flask)** - REST API и бизнес-логика
2. **Frontend (HTML/CSS/JS)** - Веб-интерфейс пользователя
3. **Services** - Интеграции и вспомогательные сервисы

## Диаграмма архитектуры

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                           │
│                   (HTML/CSS/JavaScript)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Flask Web Application                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Routes (routes.py)                                          │
│  ├─ /api/projects       (CRUD)                              │
│  ├─ /api/versions       (Read, History)                     │
│  ├─ /api/updates        (Check, History)                    │
│  ├─ /api/notifications  (Read, Mark as Read)                │
│  └─ /api/statistics     (Get Stats)                         │
│                                                               │
│  Services:                                                    │
│  ├─ github_service.py   → GitHub API Integration            │
│  ├─ pypi_service.py     → PyPI API Integration              │
│  ├─ version_checker.py  → Version Comparison Logic          │
│  └─ notifier.py         → Notification Service              │
│                                                               │
│  Models (models.py)                                          │
│  ├─ Project                                                  │
│  ├─ Version                                                  │
│  └─ Update                                                   │
│                                                               │
└──────────────┬───────────────────────────────────┬───────────┘
               │                                   │
               │                                   │
         SQLite/PostgreSQL                  External APIs
         Database                          (GitHub, PyPI)
         (version_tracker.db)
```

## Структура слоёв

### 1. Presentation Layer (Слой представления)

**Файлы:**
- `templates/base.html` - Базовый шаблон
- `templates/index.html` - Главная страница
- `templates/projects.html` - Список проектов
- `templates/project.html` - Детальный просмотр проекта
- `static/css/style.css` - Стили
- `static/js/main.js` - JavaScript функционал

**Ответственность:**
- Отображение данных пользователю
- Обработка пользовательских взаимодействий
- Отправка запросов к API

### 2. API Layer (API слой)

**Файл:** `routes.py`

**Endpoints:**
```
GET    /api/projects              - Получить все проекты
POST   /api/projects              - Создать проект
GET    /api/projects/<id>         - Получить проект
PUT    /api/projects/<id>         - Обновить проект
DELETE /api/projects/<id>         - Удалить проект

GET    /api/projects/<id>/versions        - Версии проекта
GET    /api/projects/<id>/latest-version  - Последняя версия

POST   /api/projects/<id>/check-update    - Проверить обновление
GET    /api/updates/history               - История обновлений
GET    /api/projects/<id>/updates         - Обновления проекта

GET    /api/notifications/unread          - Непрочитанные уведомления
POST   /api/notifications/mark-read/<name> - Отметить прочитанные

GET    /api/statistics            - Статистика системы
```

### 3. Business Logic Layer (Слой бизнес-логики)

**Сервисы:**

#### github_service.py
```python
class GitHubService:
    - get_releases()
    - get_latest_release()
    - get_tags()
    - parse_repo_url()
    - extract_version_info()
```

Интегрирует GitHub REST API для получения информации о releases.

#### pypi_service.py
```python
class PyPIService:
    - get_package_info()
    - get_latest_version()
    - get_release_history()
    - extract_version_info()
```

Интегрирует PyPI JSON API для получения информации о пакетах.

#### version_checker.py
```python
class VersionChecker:
    - compare_versions()
    - is_newer()
    - normalize_version()
```

Логика сравнения и анализа версий (использует packaging).

#### notifier.py
```python
class NotificationService:
    - notify_update()
    - get_unread_notifications()
    - mark_as_read()
    - clear_notifications()
```

Управление уведомлениями о новых версиях.

### 4. Data Access Layer (Слой доступа к данным)

**Файл:** `models.py`

```python
class Project(db.Model):
    - Основная сущность отслеживаемого проекта
    - Связь: 1 Project → Many Versions
    - Связь: 1 Project → Many Updates

class Version(db.Model):
    - История всех версий проекта
    - Хранит информацию о каждом release

class Update(db.Model):
    - История всех обновлений
    - Записывает переходы между версиями
```

## Data Flow

### Сценарий 1: Добавление нового проекта

```
User Interface
      │
      │ POST /api/projects
      ▼
   routes.py (create_project)
      │
      │ validate input
      ▼
   models.py (Project)
      │
      │ create & save
      ▼
   Database
      │
      │ response
      ▼
   Frontend
```

### Сценарий 2: Проверка обновлений

```
Frontend
   │
   │ POST /api/projects/<id>/check-update
   ▼
routes.py (check_update)
   │
   ├─ Get project from DB
   │
   ├─ if github_repo exists
   │  └─ github_service.get_latest_release()
   │     └─ Call GitHub API
   │        └─ Parse response
   │
   ├─ if pypi_package exists
   │  └─ pypi_service.get_package_info()
   │     └─ Call PyPI API
   │        └─ Parse response
   │
   ├─ version_checker.compare_versions()
   │  └─ Determine update type (major/minor/patch)
   │
   ├─ Create Version & Update records
   │
   ├─ notification_service.notify_update()
   │
   └─ Save to Database
      │
      └─ Return response
         │
         ▼
      Frontend displays result
```

## Базовые операции

### 1. CRUD для Projects

```python
# Create
project = Project(name='Flask', github_repo='...')
db.session.add(project)
db.session.commit()

# Read
project = Project.query.get(1)
projects = Project.query.all()

# Update
project.current_version = '2.0.0'
db.session.commit()

# Delete
db.session.delete(project)
db.session.commit()
```

### 2. Проверка обновления

```python
# 1. Получить информацию о проекте
project = Project.query.get(project_id)

# 2. Получить последнюю версию из источника
release = github_service.get_latest_release(owner, repo)

# 3. Сравнить версии
update_type = version_checker.compare_versions(
    project.current_version, 
    release.version
)

# 4. Если есть обновление - создать записи
if update_type:
    version = Version(version_number=release.version)
    update = Update(old_version=..., new_version=...)
    db.session.add(version)
    db.session.add(update)
    db.session.commit()
```

## Конфигурация

**config.py** содержит три конфигурации:

```python
class Config:           # Base config
class DevelopmentConfig # Development config
class TestingConfig     # Testing config
class ProductionConfig  # Production config
```

Параметры:
- `DEBUG` - Режим отладки
- `DATABASE_URI` - Строка подключения к БД
- `GITHUB_TOKEN` - Токен для GitHub API
- `UPDATE_CHECK_INTERVAL` - Интервал проверок (часы)

## Безопасность

### Input Validation
- Все POST/PUT данные валидируются
- Используется Flask-CORS для контроля CORS

### Error Handling
- Все ошибки логируются
- Безопасные сообщения об ошибках возвращаются клиентам

### Database Security
- SQL Injection protection через SQLAlchemy ORM
- Параметризованные запросы

## Производительность

### Оптимизация БД
- Индексы на часто используемых полях
- Lazy loading для отношений

### Кеширование
- Frontend кеширует данные в памяти браузера
- Можно добавить Redis для серверного кеша

### Асинхронные операции
- Внешние API вызовы имеют timeout (10 сек)
- Можно добавить Celery для фоновых задач

## Масштабируемость

### Горизонтальное масштабирование
- Stateless API design
- Можно развернуть за load balancer
- Требуется shared session storage (Redis)

### Вертикальное масштабирование
- Оптимизация запросов к БД
- Индексирование
- Connection pooling

## Мониторинг

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

### Health Check
```
GET /health
```

### Metrics
```
GET /api/statistics
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│           User Browser                  │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │   Reverse Proxy │
        │    (Nginx)      │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   Load Balancer │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ App 1  │  │ App 2  │  │ App N  │
│(5000)  │  │(5001)  │  │(500N)  │
└───┬────┘  └───┬────┘  └───┬────┘
    │          │          │
    └──────────┼──────────┘
               │
        ┌──────▼──────┐
        │  Shared DB  │
        │ PostgreSQL  │
        └─────────────┘
```

## Расширяемость

### Добавление нового источника версий

1. Создайте новый сервис: `services/npm_service.py`
2. Реализуйте метод `get_latest_version()`
3. Добавьте поле в модель Project: `npm_package`
4. Добавьте логику в `routes.py` (check_update)

### Добавление нового типа уведомлений

1. Расширьте `notifier.py`
2. Добавьте методы отправки (email, webhook, etc.)
3. Обновите конфигурацию
4. Интегрируйте в API

## Testing

```
Unit Tests      → test_models.py, test_services.py
Integration     → test_routes.py
E2E Tests       → (Selenium, Cypress)
```

## Версионирование API

Текущая версия: **v1.0**

Будущие версии могут быть достаточны через:
- URL versioning: `/api/v2/projects`
- Header versioning: `Accept: application/vnd.api+json;version=2`
