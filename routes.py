from flask import Blueprint, request, jsonify, current_app
from models import db, Project, Version, Update
from services.github_service import GitHubService
from services.pypi_service import PyPIService
from services.version_checker import VersionChecker
from services.notifier import notification_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

github_service = GitHubService(token=None)
pypi_service = PyPIService()
version_checker = VersionChecker()

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    # Вывод всех проектов
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    pagination = Project.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'projects': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/projects', methods=['POST'])
def create_project():
    # Создание нового проекта
    data = request.get_json() or {}

    # Валидация
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    if Project.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Project with this name already exists'}), 400
    
    try:
        # Создание проекта
        project = Project(
            name=data['name'],
            description=data.get('description'),
            github_repo=data.get('github_repo'),
            pypi_package=data.get('pypi_package'),
            category=data.get('category'),
            current_version=data.get('current_version'),
            notify_on_update=data.get('notify_on_update', True)
        )
        
        db.session.add(project)
        db.session.commit()
        
        logger.info(f'Project created: {project.name}')
        return jsonify(project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating project: {e}')
        return jsonify({'error': str(e)}), 400

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    # Получить конкретный проект
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict())

@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    # Обновить проект
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}
    
    try:
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'github_repo' in data:
            project.github_repo = data['github_repo']
        if 'pypi_package' in data:
            project.pypi_package = data['pypi_package']
        if 'category' in data:
            project.category = data['category']
        if 'current_version' in data:
            project.current_version = data['current_version']
        if 'active' in data:
            project.active = data['active']
        if 'notify_on_update' in data:
            project.notify_on_update = data['notify_on_update']
        
        db.session.commit()
        logger.info(f'Project updated: {project.name}')
        return jsonify(project.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating project: {e}')
        return jsonify({'error': str(e)}), 400

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    # Удалить проект
    project = Project.query.get_or_404(project_id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        logger.info(f'Project deleted: {project.name}')
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting project: {e}')
        return jsonify({'error': str(e)}), 400

@api_bp.route('/projects/<int:project_id>/versions', methods=['GET'])
def get_versions(project_id):
    # Узнать версию
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    pagination = Version.query.filter_by(project_id=project_id).order_by(
        Version.release_date.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'versions': [v.to_dict() for v in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/projects/<int:project_id>/latest-version', methods=['GET'])
def get_latest_version(project_id):
    # Получить информацию о последнем релизе
    project = Project.query.get_or_404(project_id)
    
    latest = Version.query.filter_by(project_id=project_id, is_latest=True).first()
    
    if latest:
        return jsonify(latest.to_dict())
    else:
        return jsonify({'error': 'No versions found'}), 404

@api_bp.route('/projects/<int:project_id>/check-update', methods=['POST'])
def check_update(project_id):
    # Проверить обновления
    project = Project.query.get_or_404(project_id)
    
    try:
        update_info = None
        if project.github_repo:
            owner, repo = github_service.parse_repo_url(project.github_repo)
            if owner and repo:
                release = github_service.get_latest_release(owner, repo)
                if release:
                    update_info = github_service.extract_version_info(release)
        
        # Проверить PyPI
        if project.pypi_package and not update_info:
            latest_version = pypi_service.get_latest_version(project.pypi_package)
            if latest_version:
                update_info = pypi_service.extract_version_info(project.pypi_package)
        
        if update_info:
            new_version = update_info['version_number']
            existing = Version.query.filter_by(
                project_id=project_id,
                version_number=new_version
            ).first()
            
            if not existing:
                version = Version(
                    project_id=project_id,
                    version_number=new_version,
                    release_date=update_info.get('release_date'),
                    download_url=update_info.get('download_url'),
                    is_prerelease=update_info.get('is_prerelease', False),
                    is_latest=True
                )
                Version.query.filter_by(project_id=project_id, is_latest=True).update({'is_latest': False})
                
                db.session.add(version)
                if project.current_version:
                    update_type = version_checker.compare_versions(
                        project.current_version,
                        new_version
                    )
                    
                    if update_type:
                        update = Update(
                            project_id=project_id,
                            old_version=project.current_version,
                            new_version=new_version,
                            update_type=update_type,
                            description=update_info.get('description')
                        )
                db.session.add(update)
                notification_service.notify_update(
                    project.name,
                    project.current_version,
                    new_version
                )
                
                project.current_version = new_version
                project.latest_version = new_version
                project.latest_release_date = update_info.get('release_date')
                project.last_checked = datetime.utcnow()
                
                db.session.commit()
                logger.info(f'Update detected for {project.name}: {new_version}')
                
                return jsonify({
                    'message': 'Update found',
                    'version': version.to_dict()
                })
        
        project.last_checked = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'No updates available'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error checking updates for project {project_id}: {e}')
        return jsonify({'error': str(e)}), 400

@api_bp.route('/updates/history', methods=['GET'])
def get_updates_history():
    # Получить историю обновлений
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    pagination = Update.query.order_by(Update.detected_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'updates': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/projects/<int:project_id>/updates', methods=['GET'])
def get_project_updates(project_id):
    # Получить обновление конкретного проекта
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    pagination = Update.query.filter_by(project_id=project_id).order_by(
        Update.detected_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'updates': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/notifications/unread', methods=['GET'])
def get_unread_notifications():
    # Получить непрочитанные уведомления
    notifications = notification_service.get_unread_notifications()
    return jsonify({
        'notifications': notifications,
        'count': len(notifications)
    })

@api_bp.route('/notifications/mark-read/<project_name>', methods=['POST'])
def mark_notification_read(project_name):
    # Сделать уведомления прочитанными
    notification_service.mark_as_read(project_name)
    return jsonify({'message': 'Notifications marked as read'})

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    # Получить статистику системы
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(active=True).count()
    total_versions = Version.query.count()
    total_updates = Update.query.count()
    
    return jsonify({
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_versions': total_versions,
        'total_updates': total_updates,
        'timestamp': datetime.utcnow().isoformat()
    })
