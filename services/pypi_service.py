# MIT License

import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PyPIService:
    """Сервис для взаимодействия с PyPI API"""
    
    def __init__(self, base_url: str = 'https://pypi.org/pypi'):
        self.base_url = base_url
    
    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Получить информацию о пакете из PyPI"""
        try:
            url = f'{self.base_url}/{package_name}/json'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f'Ошибка при загрузке информации PyPI для {package_name}: {e}')
            return None
    
    def get_latest_version(self, package_name: str) -> Optional[str]:
        """Получить последнюю версию пакета"""
        try:
            info = self.get_package_info(package_name)
            if info:
                return info.get('info', {}).get('version')
        except Exception as e:
            logger.error(f'Ошибка при получении последней версии для {package_name}: {e}')
        return None
    
    def get_release_history(self, package_name: str) -> List[Dict]:
        """Получить историю релизов пакета"""
        try:
            info = self.get_package_info(package_name)
            if info:
                releases = info.get('releases', {})
                version_list = []
                for version, files in releases.items():
                    if files:  # Включать только версии с файлами
                        version_list.append({
                            'version_number': version,
                            'release_date': datetime.fromisoformat(
                                files[0].get('upload_time_iso_8601', '').split('T')[0]
                            ) if files[0].get('upload_time_iso_8601') else None,
                            'files_count': len(files)
                        })
                return sorted(version_list, key=lambda x: x.get('release_date') or datetime.min, reverse=True)
        except Exception as e:
            logger.error(f'Ошибка при получении истории релизов для {package_name}: {e}')
        return []
    
    def extract_version_info(self, package_name: str) -> Optional[Dict]:
        """Извлечь информацию о версии из PyPI"""
        try:
            info = self.get_package_info(package_name)
            if info:
                pkg_info = info.get('info', {})
                return {
                    'version_number': pkg_info.get('version'),
                    'release_date': None,  # PyPI не предоставляет точные даты релизов в JSON API
                    'download_url': pkg_info.get('project_url'),
                    'is_prerelease': False,
                    'description': pkg_info.get('summary', '')
                }
        except Exception as e:
            logger.error(f'Ошибка при извлечении информации PyPI для {package_name}: {e}')
        return None
