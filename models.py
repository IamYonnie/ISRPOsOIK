# MIT License

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    """Model for tracked software projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    github_repo = db.Column(db.String(255), nullable=True, unique=True)
    pypi_package = db.Column(db.String(255), nullable=True, unique=True)
    category = db.Column(db.String(100), nullable=True)  # e.g., 'framework', 'library', 'tool'
    
    # Tracking info
    current_version = db.Column(db.String(50), nullable=True)
    latest_version = db.Column(db.String(50), nullable=True)
    latest_release_date = db.Column(db.DateTime, nullable=True)
    
    # Configuration
    active = db.Column(db.Boolean, default=True, index=True)
    notify_on_update = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    versions = db.relationship('Version', backref='project', lazy=True, cascade='all, delete-orphan')
    updates = db.relationship('Update', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'github_repo': self.github_repo,
            'pypi_package': self.pypi_package,
            'category': self.category,
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'latest_release_date': self.latest_release_date.isoformat() if self.latest_release_date else None,
            'active': self.active,
            'notify_on_update': self.notify_on_update,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'version_count': len(self.versions),
            'update_count': len(self.updates)
        }


class Version(db.Model):
    """Model for software versions"""
    __tablename__ = 'versions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    
    version_number = db.Column(db.String(50), nullable=False)
    release_date = db.Column(db.DateTime, nullable=True)
    download_url = db.Column(db.String(500), nullable=True)
    changelog_url = db.Column(db.String(500), nullable=True)
    
    # Metadata
    is_prerelease = db.Column(db.Boolean, default=False)
    is_latest = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Version {self.version_number}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'version_number': self.version_number,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'download_url': self.download_url,
            'changelog_url': self.changelog_url,
            'is_prerelease': self.is_prerelease,
            'is_latest': self.is_latest,
            'created_at': self.created_at.isoformat()
        }


class Update(db.Model):
    """Model for tracking version updates"""
    __tablename__ = 'updates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    
    old_version = db.Column(db.String(50), nullable=True)
    new_version = db.Column(db.String(50), nullable=False)
    
    # Update info
    description = db.Column(db.Text, nullable=True)
    update_type = db.Column(db.String(20), nullable=True)  # 'major', 'minor', 'patch'
    
    # Metadata
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    release_date = db.Column(db.DateTime, nullable=True)
    
    # Notification status
    notified = db.Column(db.Boolean, default=False)
    notified_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Update {self.old_version} -> {self.new_version}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'old_version': self.old_version,
            'new_version': self.new_version,
            'description': self.description,
            'update_type': self.update_type,
            'detected_at': self.detected_at.isoformat(),
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'notified': self.notified,
            'notified_at': self.notified_at.isoformat() if self.notified_at else None
        }
