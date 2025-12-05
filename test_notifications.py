#!/usr/bin/env python
"""
Test notifications endpoint
"""

import os
import sys
os.environ['FLASK_ENV'] = 'development'

from app import create_app

app = create_app('development')

with app.app_context():
    with app.test_client() as client:
        print("=" * 60)
        print("Testing Notifications API")
        print("=" * 60)
        
        # Get unread notifications
        print("\nGET /api/notifications/unread")
        response = client.get('/api/notifications/unread')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Mark as read
        print("\nPOST /api/notifications/mark-read/test")
        response = client.post('/api/notifications/mark-read/test')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
