# MIT License

import pytest
import json
from models import db, Project

class TestProjectRoutes:
    """Tests for project API routes"""
    
    def test_get_projects_empty(self, client):
        """Test getting empty project list"""
        response = client.get('/api/projects')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['projects'] == []
        assert data['total'] == 0
    
    def test_create_project(self, client, app):
        """Test creating a project"""
        with app.app_context():
            response = client.post('/api/projects', json={
                'name': 'Test Project',
                'description': 'Test Description',
                'category': 'library'
            })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['name'] == 'Test Project'
            assert data['description'] == 'Test Description'
    
    def test_create_project_duplicate(self, client, app):
        """Test creating duplicate project"""
        with app.app_context():
            # Create first project
            client.post('/api/projects', json={'name': 'Test Project'})
            
            # Try to create duplicate
            response = client.post('/api/projects', json={'name': 'Test Project'})
            assert response.status_code == 400
    
    def test_get_project(self, client, app):
        """Test getting a specific project"""
        with app.app_context():
            project = Project(name='Test Project')
            db.session.add(project)
            db.session.commit()
            project_id = project.id
            
            response = client.get(f'/api/projects/{project_id}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Test Project'
    
    def test_delete_project(self, client, app):
        """Test deleting a project"""
        with app.app_context():
            project = Project(name='Test Project')
            db.session.add(project)
            db.session.commit()
            project_id = project.id
            
            response = client.delete(f'/api/projects/{project_id}')
            assert response.status_code == 200
            
            # Verify deletion
            deleted_project = Project.query.get(project_id)
            assert deleted_project is None

class TestHealthRoute:
    """Tests for health check route"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
