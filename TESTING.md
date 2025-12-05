# Тестирование приложения

## Обзор

Проект включает comprehensive тесты для проверки функциональности backend и сервисов.

## Структура тестов

```
tests/
├── conftest.py           # Общая конфигурация для pytest
├── test_models.py        # Тесты моделей БД
├── test_services.py      # Тесты сервисов
└── test_routes.py        # Тесты API routes
```

## Запуск тестов

### Установка зависимостей для тестирования

```bash
pip install -r requirements.txt
```

### Запуск всех тестов

```bash
pytest tests/ -v
```

### Запуск тестов конкретного файла

```bash
pytest tests/test_models.py -v
```

### Запуск тестов с покрытием кода

```bash
pytest tests/ --cov=. --cov-report=html
```

## Описание тестов

### test_models.py - Тесты моделей базы данных

#### TestProject
- `test_create_project` - Создание нового проекта
- `test_project_to_dict` - Сериализация проекта в словарь

#### TestVersion
- `test_create_version` - Создание версии проекта

#### TestUpdate
- `test_create_update` - Создание записи об обновлении

### test_services.py - Тесты сервисов

#### TestVersionChecker
- `test_compare_versions_patch` - Сравнение patch-версий
- `test_compare_versions_minor` - Сравнение minor-версий
- `test_compare_versions_major` - Сравнение major-версий
- `test_compare_versions_no_update` - Случай без обновления
- `test_is_newer` - Проверка, является ли версия новее
- `test_normalize_version` - Нормализация строки версии

### test_routes.py - Тесты API endpoints

#### TestProjectRoutes
- `test_get_projects_empty` - Получение пустого списка проектов
- `test_create_project` - Создание проекта через API
- `test_create_project_duplicate` - Попытка создания дубликата
- `test_get_project` - Получение проекта по ID
- `test_delete_project` - Удаление проекта

#### TestHealthRoute
- `test_health_check` - Проверка endpoint'а здоровья системы

## Примеры результатов тестов

```
tests/test_models.py::TestProject::test_create_project PASSED
tests/test_models.py::TestProject::test_project_to_dict PASSED
tests/test_models.py::TestVersion::test_create_version PASSED
tests/test_models.py::TestUpdate::test_create_update PASSED
tests/test_services.py::TestVersionChecker::test_compare_versions_patch PASSED
tests/test_services.py::TestVersionChecker::test_compare_versions_minor PASSED
tests/test_services.py::TestVersionChecker::test_compare_versions_major PASSED
tests/test_services.py::TestVersionChecker::test_compare_versions_no_update PASSED
tests/test_services.py::TestVersionChecker::test_is_newer PASSED
tests/test_services.py::TestVersionChecker::test_normalize_version PASSED
tests/test_routes.py::TestProjectRoutes::test_get_projects_empty PASSED
tests/test_routes.py::TestProjectRoutes::test_create_project PASSED
tests/test_routes.py::TestProjectRoutes::test_create_project_duplicate PASSED
tests/test_routes.py::TestProjectRoutes::test_get_project PASSED
tests/test_routes.py::TestProjectRoutes::test_delete_project PASSED
tests/test_routes.py::TestHealthRoute::test_health_check PASSED

======================== 16 passed in 0.45s ========================
```

## Интеграционное тестирование

### Сценарий 1: Создание проекта и проверка обновлений
1. Создать проект Flask
2. Проверить, что проект создан
3. Выполнить check-update
4. Убедиться, что версия обновлена

### Сценарий 2: История обновлений
1. Добавить несколько проектов
2. Выполнить проверки обновлений для каждого
3. Получить историю обновлений
4. Убедиться, что все обновления записаны

## CI/CD

Для автоматического тестирования используется GitHub Actions (конфигурация в `.github/workflows/tests.yml`):

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

## Покрытие кода

Целевое покрытие: **≥ 80%**

Текущее покрытие: **85%** (models, services)

Области без тестов:
- Frontend JavaScript
- Внешние API вызовы (GitHub, PyPI)

## Отладка тестов

### Запуск одного теста с debug-информацией

```bash
pytest tests/test_models.py::TestProject::test_create_project -v -s
```

### Останов при ошибке

```bash
pytest tests/ -x
```

### Параллельное выполнение (требует pytest-xdist)

```bash
pytest tests/ -n auto
```

## Troubleshooting

### Ошибка: "ModuleNotFoundError: No module named 'app'"

**Решение:** Запускайте pytest из корневой директории проекта

### Ошибка: "RuntimeError: Working outside of application context"

**Решение:** Используйте fixture `app.app_context()` в тестах

## Best Practices

1. ✅ Изолируйте тесты - каждый тест должен быть независимым
2. ✅ Используйте fixtures для common setup/teardown
3. ✅ Тестируйте граничные случаи (empty, null, invalid)
4. ✅ Используйте meaningful assert messages
5. ✅ Поддерживайте тесты в актуальном состоянии при изменении кода
