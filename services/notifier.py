# MIT License

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications about version updates"""
    
    def notify_update(self, project_name: str, old_version: str, new_version: str) -> Dict:
        """Create a notification about a version update"""
        # Import here to avoid circular imports
        from models import db, Update, Project
        
        try:
            project = Project.query.filter_by(name=project_name).first()
            if not project:
                logger.warning(f'Project not found: {project_name}')
                return {}
            
            logger.info(f'Notification created: {project_name} updated from {old_version} to {new_version}')
            return {
                'project': project_name,
                'old_version': old_version,
                'new_version': new_version,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f'Error in notify_update: {e}')
            return {}
    
    def get_unread_notifications(self) -> List[Dict]:
        """Get all unread notifications from database"""
        from models import Update, Project
        
        try:
            # Get updates that haven't been marked as read yet
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
            logger.error(f'Error in get_unread_notifications: {e}')
            return []
    
    def mark_as_read(self, project_name: str) -> None:
        """Mark notifications as read for a project"""
        from models import db, Update, Project
        
        try:
            project = Project.query.filter_by(name=project_name).first()
            if project:
                # Mark all updates for this project as notified
                Update.query.filter_by(project_id=project.id, notified=False).update({
                    'notified': True, 
                    'notified_at': datetime.utcnow()
                })
                db.session.commit()
                logger.info(f'Marked notifications as read for {project_name}')
        except Exception as e:
            logger.error(f'Error in mark_as_read: {e}')
    
    def clear_notifications(self) -> None:
        """Clear all notifications"""
        from models import db, Update
        
        try:
            Update.query.filter_by(notified=False).update({
                'notified': True, 
                'notified_at': datetime.utcnow()
            })
            db.session.commit()
            logger.info('Cleared all notifications')
        except Exception as e:
            logger.error(f'Error in clear_notifications: {e}')

# Global notification service instance
notification_service = NotificationService()
