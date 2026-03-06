# MIT License

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class NotificationService:
    """Сервис для обработки уведомлений об обновлениях версий"""
    
    def notify_update(self, project_name: str, old_version: str, new_version: str) -> Dict:
        """Создать уведомление об обновлении версии"""
        # Импортировать здесь, чтобы избежать циклических импортов
        from models import db, Update, Project
        
        try:
            project = Project.query.filter_by(name=project_name).first()
            if not project:
                logger.warning(f'Проект не найден: {project_name}')
                return {}
            
            logger.info(f'Создано уведомление: {project_name} обновился с {old_version} на {new_version}')
            return {
                'project': project_name,
                'old_version': old_version,
                'new_version': new_version,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f'Ошибка в notify_update: {e}')
            return {}
    
    def get_unread_notifications(self) -> List[Dict]:
        """Получить все непрочитанные уведомления из базы данных"""
        from models import Update, Project
        
        try:
            # Получить обновления, которые еще не были отмечены как прочитанные
            updates = Update.query.filter_by(notified=False).all()
            
            notifications = []
            for update in updates:
                project = Project.query.get(update.project_id)
                if project:
                    notifications.append({
                        'project': project.name,
                        'old_version': update.old_version,
                        'new_version': update.new_version,
                        'update_type': update.update_type,
                        'detected_at': update.detected_at.isoformat() if update.detected_at else None
                    })
            
            return notifications
        except Exception as e:
            logger.error(f'Ошибка в get_unread_notifications: {e}')
            return []
    
    def mark_as_read(self, project_name: str) -> None:
        """Отметить уведомления как прочитанные для проекта"""
        from models import db, Update, Project
        
        try:
            project = Project.query.filter_by(name=project_name).first()
            if project:
                # Отметить все обновления этого проекта как уведомленные
                Update.query.filter_by(project_id=project.id, notified=False).update({
                    'notified': True, 
                    'notified_at': datetime.utcnow()
                })
                db.session.commit()
                logger.info(f'Уведомления отмечены как прочитанные для {project_name}')
        except Exception as e:
            logger.error(f'Ошибка в mark_as_read: {e}')
    
    def clear_notifications(self) -> None:
        """Очистить все уведомления"""
        from models import db, Update
        
        try:
            Update.query.filter_by(notified=False).update({
                'notified': True, 
                'notified_at': datetime.utcnow()
            })
            db.session.commit()
            logger.info('Все уведомления очищены')
        except Exception as e:
            logger.error(f'Ошибка в clear_notifications: {e}')

# Global notification service instance
notification_service = NotificationService()
