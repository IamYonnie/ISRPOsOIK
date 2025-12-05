# Руководство по установке и развертыванию

## Системные требования

- **Python 3.11 или 3.12** ⚠️ **ВАЖНО: Python 3.13 несовместим с SQLAlchemy, используйте 3.11 или 3.12**
- pip (Python package manager)
- Git
- SQLite (встроено в Python) или PostgreSQL для production

## Локальная установка (Development)

### ⚠️ Проблема: Python 3.13 - AssertionError при импорте

Если вы получили ошибку:
```
AssertionError: ... super(Generic, cls).__init_subclass__(*args, **kwargs)
```

**Решение:** Используйте Python 3.11 или 3.12:

```bash
# Проверить установленные версии
python --version

# Если нужно установить другую версию:
# Windows: Загрузите с python.org и установите 3.11 или 3.12 параллельно
# Mac: brew install python@3.11
# Linux: sudo apt install python3.11
```

Если у вас уже установлены несколько версий Python:

```bash
# Используйте 3.11 явно
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
python3.11 -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Varyusha
```

### 2. Создание виртуального окружения

**На Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**На Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**На Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Конфигурация

Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-for-dev
DEBUG=True
DATABASE_URL=sqlite:///version_tracker.db
GITHUB_TOKEN=your_github_token  # Опционально
UPDATE_CHECK_INTERVAL=6
```

### 5. Инициализация базы данных

```bash
python -c "from app import create_app; app = create_app(); app.app_context().push(); from models import db; db.create_all()"
```

### 6. Запуск приложения

**Способ 1 (Рекомендуется): Использование run.py**
```bash
python run.py
```

**Способ 2: Запуск через Flask напрямую**
```bash
python app.py
```

Приложение будет доступно по адресу: **http://localhost:5000**

Используйте **Ctrl+C** для остановки сервера.

## Docker развертывание

### 1. Сборка образа

```bash
docker build -t version-tracker:latest .
```

### 2. Запуск контейнера

```bash
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DEBUG=False \
  -v version_tracker_db:/app/data \
  --name version-tracker \
  version-tracker:latest
```

### 3. Проверка статуса

```bash
docker ps
docker logs version-tracker
```

## Production развертывание

### Использование Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:create_app()"
```

### С Nginx (reverse proxy)

**nginx.conf:**
```nginx
upstream app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/version-tracker/static/;
        expires 30d;
    }
}
```

### С PostgreSQL

Установите PostgreSQL и создайте базу:

```bash
createdb version_tracker
```

В файле `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/version_tracker
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
```

Запустите миграции:
```bash
python -c "from app import create_app; app = create_app('production'); app.app_context().push(); from models import db; db.create_all()"
```

## Systemd сервис (для Linux)

Создайте файл `/etc/systemd/system/version-tracker.service`:

```ini
[Unit]
Description=Version Tracker Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/version-tracker
Environment="PATH=/var/www/version-tracker/venv/bin"
ExecStart=/var/www/version-tracker/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl enable version-tracker
sudo systemctl start version-tracker
sudo systemctl status version-tracker
```

## SSL/TLS (HTTPS)

### С Let's Encrypt и Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

Обновите nginx конфиг для использования SSL.

## Мониторинг и логирование

### Просмотр логов

```bash
# Systemd
sudo journalctl -u version-tracker -f

# Docker
docker logs -f version-tracker
```

### Health check

```bash
curl http://localhost:5000/health
```

## Backup базы данных

### SQLite
```bash
cp version_tracker.db version_tracker.db.backup
```

### PostgreSQL
```bash
pg_dump -U user version_tracker > backup.sql
```

## Troubleshooting

### Ошибка: "Port 5000 already in use"
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Ошибка: "Module not found"
```bash
# Убедитесь, что виртуальное окружение активировано
which python  # Должен быть путь в venv

# Переустановите зависимости
pip install -r requirements.txt --upgrade
```

### Ошибка: "No module named 'flask'"
```bash
pip install Flask Flask-SQLAlchemy Flask-CORS
```

### Проблемы с БД
```bash
# Удалите старую БД и пересоздайте
rm version_tracker.db
python -c "from app import create_app; app = create_app(); app.app_context().push(); from models import db; db.create_all()"
```

## Обновление приложения

```bash
# Получите последние изменения
git pull origin master

# Установите новые зависимости
pip install -r requirements.txt --upgrade

# ПереStartуйте приложение
systemctl restart version-tracker
```

## Переменные окружения (Production)

| Переменная | Значение | Описание |
|-----------|---------|---------|
| FLASK_ENV | production | Режим production |
| DEBUG | False | Отключить режим отладки |
| SECRET_KEY | <secure-key> | Секретный ключ (32+ символа) |
| DATABASE_URL | postgresql://... | URL подключения к БД |
| GITHUB_TOKEN | <token> | GitHub Personal Access Token |
| UPDATE_CHECK_INTERVAL | 6 | Интервал проверки (часы) |

## Performance Tips

1. **Кеширование:** Используйте Redis для кеширования
2. **Асинхронные задачи:** Используйте Celery для фоновых проверок
3. **Индексирование БД:** Добавьте индексы на часто используемые колонки
4. **Compress:** Включите gzip compression в nginx

## Безопасность

1. ✅ Используйте HTTPS в production
2. ✅ Установите CORS правильно
3. ✅ Валидируйте все входные данные
4. ✅ Используйте strong SECRET_KEY
5. ✅ Регулярно обновляйте зависимости
