# MIT License

"""
Фоновые задачи для приложения Version Tracker
Автоматическая проверка версий и система уведомлений
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
app_instance = None  # Будет установлено функцией start_scheduler


def check_all_updates():
    """Проверить обновления для всех активных проектов"""
    if not app_instance:
        logger.error('App instance not set for scheduler')
        return
    
    with app_instance.app_context():
        try:
            from models import db, Project, Version, Update
            from services.github_service import GitHubService
            from services.pypi_service import PyPIService
            from services.version_checker import VersionChecker
            from services.notifier import NotificationService
            
            github_service = GitHubService()
            pypi_service = PyPIService()
            version_checker = VersionChecker()
            notification_service = NotificationService()
            
            projects = Project.query.filter_by(active=True).all()
            logger.info(f'Запуск проверки обновлений для {len(projects)} проектов')
            
            for project in projects:
                try:
                    logger.info(f'Проверка обновлений для: {project.name}')
                    check_project_updates(project, github_service, pypi_service, version_checker, notification_service)
                except Exception as e:
                    logger.error(f'Ошибка при проверке обновлений для {project.name}: {e}')
            
            logger.info(f'✓ Завершена проверка обновлений для {len(projects)} проектов')
        except Exception as e:
            logger.error(f'Error in check_all_updates: {e}')


def check_project_updates(project, github_service, pypi_service, version_checker, notification_service):
    """Проверить обновления для одного проекта"""
    from models import db, Version, Update
    
    try:
        update_info = None
        
        # Проверить GitHub
        if project.github_repo:
            try:
                owner, repo = github_service.parse_repo_url(project.github_repo)
                if owner and repo:
                    release = github_service.get_latest_release(owner, repo)
                    if release:
                        update_info = github_service.extract_version_info(release)
            except Exception as e:
                logger.warning(f'Проверка GitHub не выполнена для {project.name}: {e}')
        
        # Проверить PyPI
        if project.pypi_package and not update_info:
            try:
                latest_version = pypi_service.get_latest_version(project.pypi_package)
                if latest_version:
                    update_info = pypi_service.extract_version_info(project.pypi_package)
            except Exception as e:
                logger.warning(f'Проверка PyPI не выполнена для {project.name}: {e}')
        
        if update_info:
            new_version = update_info['version_number']
            
            # Проверить, существует ли версия
            existing = Version.query.filter_by(
                project_id=project.id,
                version_number=new_version
            ).first()
            
            if not existing:
                logger.info(f'Найдена новая версия для {project.name}: {new_version}')
                version = Version(
                    project_id=project.id,
                    version_number=new_version,
                    release_date=update_info.get('release_date'),
                    download_url=update_info.get('download_url'),
                    is_prerelease=update_info.get('is_prerelease', False),
                    is_latest=True
                )
                
                # Отметить старые версии как не последние
                Version.query.filter_by(project_id=project.id, is_latest=True).update({'is_latest': False})
                
                db.session.add(version)
                
                # Проверить, является ли это обновлением
                if project.current_version:
                    update_type = version_checker.compare_versions(
                        project.current_version,
                        new_version
                    )
                    
                    if update_type:
                        logger.info(f'Создание записи обновления {update_type} для {project.name}')
                        update = Update(
                            project_id=project.id,
                            old_version=project.current_version,
                            new_version=new_version,
                            update_type=update_type,
                            description=update_info.get('description')
                        )
                        db.session.add(update)
                        
                        # Отправить уведомление
                        notification_service.notify_update(
                            project.name,
                            project.current_version,
                            new_version
                        )
                        
                        logger.info(f'Новое обновление {update_type} для {project.name}: {new_version}')
                else:
                    logger.info(f'Текущая версия не установлена для {project.name}, не создаем запись об обновлении')
                
                project.current_version = new_version
                project.latest_version = new_version
                project.latest_release_date = update_info.get('release_date')
                project.last_checked = datetime.utcnow()
                
                db.session.commit()
    except Exception as e:
        logger.error(f'Error checking updates for {project.name}: {e}')


def start_scheduler(app):
    """Запустить фоновый планировщик"""
    global app_instance
    app_instance = app  # Сохранить экземпляр приложения для использования в check_all_updates
    
    try:
        # Получить интервал проверки обновлений из конфигурации (в секундах)
        interval = app.config.get('UPDATE_CHECK_INTERVAL', 3600)
        
        scheduler.add_job(
            func=check_all_updates,
            trigger="interval",
            seconds=interval,
            id='check_updates',
            name='Проверка обновлений проектов',
            replace_existing=True,
            misfire_grace_time=60
        )
        
        if not scheduler.running:
            scheduler.start()
            minutes = interval / 60
            logger.info(f'✓ Фоновый планировщик запущен - проверка каждые {minutes:.1f} минут')
        else:
            logger.info('Фоновый планировщик уже запущен')
            
    except Exception as e:
        logger.error(f'Ошибка при запуске планировщика: {e}')


def stop_scheduler():
    """Остановить фоновый планировщик"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info('Фоновый планировщик остановлен')
    except Exception as e:
        logger.error(f'Ошибка при остановке планировщика: {e}')
