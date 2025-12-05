# MIT License

"""
Background tasks for Version Tracker Application
Automatic version checking and notification system
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, Project
from services.github_service import GitHubService
from services.pypi_service import PyPIService
from services.version_checker import VersionChecker
from services.notifier import NotificationService
from datetime import datetime

logger = logging.getLogger(__name__)

github_service = GitHubService()
pypi_service = PyPIService()
version_checker = VersionChecker()
notification_service = NotificationService()

scheduler = BackgroundScheduler()


def check_all_updates():
    """Check updates for all active projects"""
    try:
        projects = Project.query.filter_by(active=True).all()
        
        for project in projects:
            try:
                check_project_updates(project)
            except Exception as e:
                logger.error(f'Error checking updates for {project.name}: {e}')
        
        logger.info(f'Checked updates for {len(projects)} projects')
    except Exception as e:
        logger.error(f'Error in check_all_updates: {e}')


def check_project_updates(project):
    """Check updates for a single project"""
    from models import Version, Update
    
    update_info = None
    
    # Check GitHub
    if project.github_repo:
        owner, repo = github_service.parse_repo_url(project.github_repo)
        if owner and repo:
            release = github_service.get_latest_release(owner, repo)
            if release:
                update_info = github_service.extract_version_info(release)
    
    # Check PyPI
    if project.pypi_package and not update_info:
        latest_version = pypi_service.get_latest_version(project.pypi_package)
        if latest_version:
            update_info = pypi_service.extract_version_info(project.pypi_package)
    
    if update_info:
        new_version = update_info['version_number']
        
        # Check if version already exists
        existing = Version.query.filter_by(
            project_id=project.id,
            version_number=new_version
        ).first()
        
        if not existing:
            version = Version(
                project_id=project.id,
                version_number=new_version,
                release_date=update_info.get('release_date'),
                download_url=update_info.get('download_url'),
                is_prerelease=update_info.get('is_prerelease', False),
                is_latest=True
            )
            
            # Mark old versions as not latest
            Version.query.filter_by(project_id=project.id, is_latest=True).update({'is_latest': False})
            
            db.session.add(version)
            
            # Check if it's an update
            if project.current_version:
                update_type = version_checker.compare_versions(
                    project.current_version,
                    new_version
                )
                
                if update_type:
                    update = Update(
                        project_id=project.id,
                        old_version=project.current_version,
                        new_version=new_version,
                        update_type=update_type,
                        description=update_info.get('description')
                    )
                    db.session.add(update)
                    
                    # Send notification
                    notification_service.notify_update(
                        project.name,
                        project.current_version,
                        new_version
                    )
                    
                    logger.info(f'New {update_type} update for {project.name}: {new_version}')
            
            project.current_version = new_version
            project.latest_version = new_version
            project.latest_release_date = update_info.get('release_date')
            project.last_checked = datetime.utcnow()
            
            db.session.commit()


def start_scheduler(app):
    """Start background scheduler"""
    try:
        # Get update check interval from config (in hours)
        interval = app.config.get('UPDATE_CHECK_INTERVAL', 1)
        
        scheduler.add_job(
            func=check_all_updates,
            trigger="interval",
            hours=interval,
            id='check_updates',
            name='Check for project updates',
            replace_existing=True,
            misfire_grace_time=60
        )
        
        if not scheduler.running:
            scheduler.start()
            logger.info(f'Background scheduler started - checking every {interval} hour(s)')
        else:
            logger.info('Background scheduler already running')
            
    except Exception as e:
        logger.error(f'Error starting scheduler: {e}')


def stop_scheduler():
    """Stop background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info('Background scheduler stopped')
    except Exception as e:
        logger.error(f'Error stopping scheduler: {e}')
