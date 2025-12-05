# MIT License

import pytest
from models import db, Project, Version, Update
from datetime import datetime

class TestProject:
    """Tests for Project model"""
    
    def test_create_project(self, app):
        """Test creating a project"""
        with app.app_context():
            project = Project(
                name='Test Project',
                description='Test Description',
                current_version='1.0.0'
            )
            db.session.add(project)
            db.session.commit()
            
            assert project.id is not None
            assert project.name == 'Test Project'
            assert project.active is True
    
    def test_project_to_dict(self, app):
        """Test converting project to dictionary"""
        with app.app_context():
            project = Project(
                name='Test Project',
                current_version='1.0.0',
                category='library'
            )
            db.session.add(project)
            db.session.commit()
            
            data = project.to_dict()
            assert data['name'] == 'Test Project'
            assert data['current_version'] == '1.0.0'
            assert data['category'] == 'library'

class TestVersion:
    """Tests for Version model"""
    
    def test_create_version(self, app):
        """Test creating a version"""
        with app.app_context():
            project = Project(name='Test Project')
            db.session.add(project)
            db.session.commit()
            
            version = Version(
                project_id=project.id,
                version_number='1.0.0',
                is_latest=True
            )
            db.session.add(version)
            db.session.commit()
            
            assert version.id is not None
            assert version.version_number == '1.0.0'
            assert version.is_latest is True

class TestUpdate:
    """Tests for Update model"""
    
    def test_create_update(self, app):
        """Test creating an update"""
        with app.app_context():
            project = Project(name='Test Project')
            db.session.add(project)
            db.session.commit()
            
            update = Update(
                project_id=project.id,
                old_version='1.0.0',
                new_version='1.1.0',
                update_type='minor'
            )
            db.session.add(update)
            db.session.commit()
            
            assert update.id is not None
            assert update.old_version == '1.0.0'
            assert update.new_version == '1.1.0'
            assert update.update_type == 'minor'
