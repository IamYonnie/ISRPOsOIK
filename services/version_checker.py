# MIT License

from datetime import datetime
from typing import Optional, Dict
import logging
from packaging import version as pkg_version

logger = logging.getLogger(__name__)

class VersionChecker:
    """Сервис для сравнения версий и определения обновлений"""
    
    @staticmethod
    def compare_versions(old_version: str, new_version: str) -> Optional[str]:
        """
        Сравнить две версии и вернуть тип обновления
        
        Возвращает: 'major' (основная), 'minor' (дополнительная), 'patch' (исправление), или None если версии нельзя сравнить
        """
        try:
            old = pkg_version.parse(old_version)
            new = pkg_version.parse(new_version)
            
            if new <= old:
                return None  # Это не обновление
            
            # Для версий PEP440
            if hasattr(old, 'major') and hasattr(new, 'major'):
                if new.major > old.major:
                    return 'major'
                elif new.minor > old.minor:
                    return 'minor'
                else:
                    return 'patch'
            
            # Fallback для простого сравнения
            return 'patch'
        except Exception as e:
            logger.warning(f'Ошибка при сравнении версий {old_version} и {new_version}: {e}')
            return None
    
    @staticmethod
    def is_newer(version1: str, version2: str) -> bool:
        """Проверить, является ли version1 новее version2"""
        try:
            return pkg_version.parse(version1) > pkg_version.parse(version2)
        except Exception as e:
            logger.warning(f'Ошибка при сравнении версий: {e}')
            return False
    
    @staticmethod
    def normalize_version(version_str: str) -> str:
        """Нормализировать строку версии"""
        try:
            # Удалить префикс 'v' если присутствует
            if version_str.startswith('v'):
                version_str = version_str[1:]
            return str(pkg_version.parse(version_str))
        except Exception:
            return version_str
