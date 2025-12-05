# MIT License

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications about version updates"""
    
    def __init__(self):
        self.notifications = []
    
    def notify_update(self, project_name: str, old_version: str, new_version: str) -> Dict:
        """Create a notification about a version update"""
        notification = {
            'project': project_name,
            'old_version': old_version,
            'new_version': new_version,
            'timestamp': datetime.utcnow(),
            'read': False
        }
        self.notifications.append(notification)
        logger.info(f'Notification created: {project_name} updated from {old_version} to {new_version}')
        return notification
    
    def get_unread_notifications(self) -> List[Dict]:
        """Get all unread notifications"""
        return [n for n in self.notifications if not n['read']]
    
    def mark_as_read(self, project_name: str) -> None:
        """Mark notifications as read for a project"""
        for notification in self.notifications:
            if notification['project'] == project_name:
                notification['read'] = True
    
    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notifications.clear()

# Global notification service instance
notification_service = NotificationService()
