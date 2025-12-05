#!/usr/bin/env python
"""
Debug script to test background tasks
"""

import os
import sys
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from models import db, Project, Version, Update
from background_tasks import check_all_updates
from datetime import datetime

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("Testing Background Tasks")
    print("=" * 60)
    
    # Check if there are any projects
    projects = Project.query.filter_by(active=True).all()
    print(f"\nActive projects: {len(projects)}")
    
    for project in projects:
        print(f"\n  - {project.name}")
        print(f"    GitHub: {project.github_repo}")
        print(f"    PyPI: {project.pypi_package}")
        print(f"    Current Version: {project.current_version}")
        print(f"    Latest Version: {project.latest_version}")
        print(f"    Last Checked: {project.last_checked}")
    
    # Run update check
    print("\n" + "=" * 60)
    print("Running update check...")
    print("=" * 60)
    
    try:
        check_all_updates()
        print("\n✓ Update check completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during update check: {e}")
        import traceback
        traceback.print_exc()
    
    # Check notifications
    from services.notifier import NotificationService
    notif_service = NotificationService()
    
    print("\n" + "=" * 60)
    print("Notifications")
    print("=" * 60)
    
    unread = notif_service.get_unread_notifications()
    print(f"Unread notifications: {len(unread)}")
    
    for notif in unread:
        print(f"\n  - {notif.project}")
        print(f"    {notif.old_version} → {notif.new_version}")
        print(f"    Time: {notif.detected_at}")
