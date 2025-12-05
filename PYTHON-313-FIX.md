# РЕШЕНИЕ ПРОБЛЕМЫ PYTHON 3.13

## Проблема

При использовании Python 3.13 возникает ошибка:
```
AssertionError: ... super(Generic, cls).__init_subclass__(*args, **kwargs)
```

Это происходит потому, что SQLAlchemy 2.0.23 имеет проблемы совместимости с Python 3.13.

## Решение

### Вариант 1: Используйте Python 3.11 или 3.12 (РЕКОМЕНДУЕТСЯ)

#### На Windows:

**Способ A: Использование winget (если установлен)**
```powershell
winget install Python.Python.3.11
```

**Способ B: Используя Chocolatey (если установлен)**
```powershell
choco install python311
```

**Способ C: Ручная установка**
1. Посетите https://www.python.org/downloads/
2. Загрузите Python 3.11 (последнюю версию 3.11.x)
3. Запустите installer
4. ✅ **ВАЖНО**: Отметьте "Add Python 3.11 to PATH"
5. Завершите установку

#### На Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

#### На macOS:
```bash
brew install python@3.11
```

### Проверка установки

```bash
python3.11 --version
# Вывод должен быть: Python 3.11.x или выше
```

### Создание виртуального окружения с Python 3.11

#### На Windows (PowerShell):
```powershell
python3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

#### На Linux/macOS:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Вариант 2: Используйте Docker (Альтернативный способ)

Если вы не хотите устанавливать Python 3.11, используйте Docker:

```bash
docker build -t version-tracker .
docker run -p 5000:5000 version-tracker
```

Docker image уже содержит совместимую версию Python.

## Вариант 3: Обновление SQLAlchemy (Экспериментально)

Следующие версии могут иметь лучшую поддержку Python 3.13:

```bash
pip install --upgrade SQLAlchemy
```

Но это НЕ гарантируется и не тестировалось.

## Проверка работы

После установки проверьте:

```bash
python run.py
# Должен вывести:
# ============================================================
# Version Tracker Application
# ============================================================
# Starting development server...
# Open http://localhost:5000 in your browser
# Press Ctrl+C to stop
# ============================================================
```

Затем откройте http://localhost:5000 в браузере.

## Помощь

Если всё равно не работает:

1. Проверьте `python3.11 --version` - должна быть 3.11.x
2. Убедитесь, что вирт. окружение активировано
3. Переустановите зависимости: `pip install --upgrade -r requirements.txt`
4. Попробуйте: `pip install SQLAlchemy==2.0.23 Flask==3.0.0 --force-reinstall`

## Быстрые команды

```powershell
# Windows PowerShell - Полная установка с нуля
winget install Python.Python.3.11
cd c:\Kursach\Varyusha
python3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

```bash
# Linux/macOS - Полная установка с нуля
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```
