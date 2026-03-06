# MIT License - See LICENSE file for full text

import os
from datetime import timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Базовая конфигурация"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    TESTING = False
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///version_tracker.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GitHub API
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_BASE_URL = 'https://api.github.com'
    
    # PyPI API
    PYPI_API_BASE_URL = 'https://pypi.org/pypi'
    
    # Планировщик
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'
    
    # Интервал проверки обновлений (в секундах, минимум 30)
    UPDATE_CHECK_INTERVAL = int(os.getenv('UPDATE_CHECK_INTERVAL', '3600'))
    
    # Пагинация
    ITEMS_PER_PAGE = 20
    
    # API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    
    # Убедитесь, что эти переменные установлены в продакшене
    @classmethod
    def validate(cls):
        if not os.getenv('GITHUB_TOKEN'):
            raise ValueError("GITHUB_TOKEN must be set in production")

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
