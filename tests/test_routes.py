# MIT License

import pytest
import json
from models import db, Project, Version

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
        response = client.post('/api/projects', json={
            'name': 'Test Project',
            'description': 'Test Description',
            'category': 'library'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Project'
    
    def test_create_project_missing_name(self, client):
        """Test creating project without name"""
        response = client.post('/api/projects', json={
            'description': 'Test'
        })
        assert response.status_code == 400
    
    def test_get_project(self, client, app):
        """Test getting a specific project"""
        with app.app_context():
            project = Project(name='Test', current_version='1.0.0')
            db.session.add(project)
            db.session.commit()
            project_id = project.id
        
        response = client.get(f'/api/projects/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test'
    
    def test_update_project(self, client, app):
        """Test updating a project"""
        with app.app_context():
            project = Project(name='Test', current_version='1.0.0')
            db.session.add(project)
            db.session.commit()
            project_id = project.id
        
        response = client.put(f'/api/projects/{project_id}', json={
            'description': 'Updated'
        })
        assert response.status_code == 200
    
    def test_delete_project(self, client, app):
        """Test deleting a project"""
        with app.app_context():
            project = Project(name='Test')
            db.session.add(project)
            db.session.commit()
            project_id = project.id
        
        response = client.delete(f'/api/projects/{project_id}')
        assert response.status_code == 200

class TestVersionRoutes:
    """Tests for version API routes"""
    
    def test_get_versions(self, client, app):
        """Test getting versions"""
        with app.app_context():
            project = Project(name='Test')
            db.session.add(project)
            db.session.commit()
            
            version = Version(project_id=project.id, version_number='1.0.0')
            db.session.add(version)
            db.session.commit()
            project_id = project.id
        
        response = client.get(f'/api/projects/{project_id}/versions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['versions']) == 1

class TestStatisticsRoutes:
    """Tests for statistics routes"""
    
    def test_get_statistics(self, client):
        """Test getting statistics"""
        response = client.get('/api/statistics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_projects' in data
        assert 'total_versions' in data
    
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
