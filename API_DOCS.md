# API Documentation

## Базовая информация

**Base URL:** `http://localhost:5000/api`

**Формат ответов:** JSON

**Аутентификация:** Не требуется (для базовой версии)

## Endpoints

### Projects (Проекты)

#### Получить все проекты
```
GET /api/projects
```

**Query Parameters:**
- `page` (integer, default: 1) - Номер страницы

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Flask",
      "description": "Python web framework",
      "github_repo": "https://github.com/pallets/flask",
      "pypi_package": "flask",
      "category": "framework",
      "current_version": "2.3.0",
      "latest_version": "2.3.3",
      "latest_release_date": "2023-09-30T12:00:00",
      "active": true,
      "notify_on_update": true,
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00",
      "last_checked": "2023-09-30T12:00:00",
      "version_count": 10,
      "update_count": 5
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1
}
```

#### Создать проект
```
POST /api/projects
```

**Request Body:**
```json
{
  "name": "Flask",
  "description": "Python web framework",
  "github_repo": "https://github.com/pallets/flask",
  "pypi_package": "flask",
  "category": "framework",
  "current_version": "2.3.0",
  "notify_on_update": true
}
```

**Response (201 Created):**
Same as project object above

**Error (400 Bad Request):**
```json
{
  "error": "Name is required"
}
```

#### Получить проект
```
GET /api/projects/<id>
```

**Response (200 OK):**
Project object (see above)

**Error (404 Not Found):**
```json
{
  "error": "Not found"
}
```

#### Обновить проект
```
PUT /api/projects/<id>
```

**Request Body:**
```json
{
  "name": "Flask",
  "description": "Updated description",
  "active": true
}
```

**Response (200 OK):**
Updated project object

#### Удалить проект
```
DELETE /api/projects/<id>
```

**Response (200 OK):**
```json
{
  "message": "Project deleted successfully"
}
```

### Versions (Версии)

#### Получить версии проекта
```
GET /api/projects/<project_id>/versions
```

**Query Parameters:**
- `page` (integer, default: 1) - Номер страницы

**Response (200 OK):**
```json
{
  "versions": [
    {
      "id": 1,
      "project_id": 1,
      "version_number": "2.3.3",
      "release_date": "2023-09-30T12:00:00",
      "download_url": "https://github.com/pallets/flask/releases/tag/2.3.3",
      "changelog_url": null,
      "is_prerelease": false,
      "is_latest": true,
      "created_at": "2023-09-30T12:00:00"
    }
  ],
  "total": 10,
  "pages": 1,
  "current_page": 1
}
```

#### Получить последнюю версию
```
GET /api/projects/<project_id>/latest-version
```

**Response (200 OK):**
Version object (see above)

### Updates (Обновления)

#### Проверить обновление
```
POST /api/projects/<project_id>/check-update
```

**Response (200 OK):**
```json
{
  "message": "Update found",
  "version": {
    "id": 1,
    "project_id": 1,
    "version_number": "2.3.3",
    "release_date": "2023-09-30T12:00:00",
    "download_url": "https://github.com/pallets/flask/releases/tag/2.3.3",
    "is_prerelease": false,
    "is_latest": true,
    "created_at": "2023-09-30T12:00:00"
  }
}
```

or

```json
{
  "message": "No updates available"
}
```

#### Получить историю обновлений
```
GET /api/updates/history
```

**Query Parameters:**
- `page` (integer, default: 1) - Номер страницы

**Response (200 OK):**
```json
{
  "updates": [
    {
      "id": 1,
      "project_id": 1,
      "old_version": "2.3.0",
      "new_version": "2.3.3",
      "description": "Bug fixes and improvements",
      "update_type": "patch",
      "detected_at": "2023-09-30T12:00:00",
      "release_date": "2023-09-30T12:00:00",
      "notified": true,
      "notified_at": "2023-09-30T12:00:01"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1
}
```

#### Получить обновления проекта
```
GET /api/projects/<project_id>/updates
```

**Query Parameters:**
- `page` (integer, default: 1) - Номер страницы

**Response (200 OK):**
Same as history above

### Notifications (Уведомления)

#### Получить непрочитанные уведомления
```
GET /api/notifications/unread
```

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "project": "Flask",
      "old_version": "2.3.0",
      "new_version": "2.3.3",
      "timestamp": "2023-09-30T12:00:00"
    }
  ],
  "count": 1
}
```

#### Отметить уведомления как прочитанные
```
POST /api/notifications/mark-read/<project_name>
```

**Response (200 OK):**
```json
{
  "message": "Notifications marked as read"
}
```

### Statistics (Статистика)

#### Получить статистику системы
```
GET /api/statistics
```

**Response (200 OK):**
```json
{
  "total_projects": 10,
  "active_projects": 8,
  "total_versions": 100,
  "total_updates": 50,
  "timestamp": "2023-09-30T12:00:00"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | OK          |
| 201  | Created     |
| 400  | Bad Request |
| 404  | Not Found   |
| 500  | Server Error|

## Rate Limiting

В базовой версии ограничение запросов не применяется.

## Error Handling

Все ошибки возвращаются в формате JSON:

```json
{
  "error": "Error message describing the problem"
}
```

## Examples

### Пример 1: Добавить проект Flask
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flask",
    "github_repo": "https://github.com/pallets/flask",
    "pypi_package": "flask",
    "current_version": "2.3.0"
  }'
```

### Пример 2: Проверить обновление
```bash
curl -X POST http://localhost:5000/api/projects/1/check-update
```

### Пример 3: Получить все проекты
```bash
curl http://localhost:5000/api/projects
```

## Версионирование API

Текущая версия API: **v1.0**

В будущих версиях возможны изменения в структуре ответов.
