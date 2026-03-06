# MIT License

import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Сервис для взаимодействия с GitHub API"""
    
    def __init__(self, token: Optional[str] = None, base_url: str = 'https://api.github.com'):
        self.token = token
        self.base_url = base_url
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки запроса"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'VersionTracker/1.0'
        }
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        return headers
    
    def get_releases(self, owner: str, repo: str) -> List[Dict]:
        """Получить все релизы GitHub репозитория"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/releases'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка при загрузке релизов из {owner}/{repo}: {e}')
            return []
    
    def get_latest_release(self, owner: str, repo: str) -> Optional[Dict]:
        """Получить последний релиз репозитория"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/releases/latest'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f'Релизы не найдены для {owner}/{repo}: {e}')
            return None
    
    def get_tags(self, owner: str, repo: str) -> List[Dict]:
        """Получить все теги репозитория"""
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/tags'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка при загрузке тегов из {owner}/{repo}: {e}')
            return []
    
    def parse_repo_url(self, repo_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Распарсить URL GitHub репозитория в имя владельца и названия репозитория"""
        try:
            # Удалить суффикс .git если присутствует
            repo_url = repo_url.rstrip('/')
            if repo_url.endswith('.git'):
                repo_url = repo_url[:-4]
            
            # Извлечь владельца и репозиторий из различных форматов URL
            if 'github.com' in repo_url:
                parts = repo_url.split('/')
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo = parts[-1]
                    return owner, repo
        except Exception as e:
            logger.error(f'Ошибка при парсинге GitHub URL {repo_url}: {e}')
        
        return None, None
    
    def extract_version_info(self, release: Dict) -> Dict:
        """Извлечь информацию о версии из GitHub релиза"""
        return {
            'version_number': release.get('tag_name', 'unknown'),
            'release_date': datetime.fromisoformat(
                release.get('published_at', '').replace('Z', '+00:00')
            ) if release.get('published_at') else None,
            'download_url': release.get('html_url'),
            'is_prerelease': release.get('prerelease', False),
            'description': release.get('body', '')
        }
