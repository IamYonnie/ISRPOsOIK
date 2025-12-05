# MIT License

import pytest
from services.version_checker import VersionChecker
from services.github_service import GitHubService

class TestVersionChecker:
    """Tests for VersionChecker service"""
    
    def test_compare_versions_patch(self):
        """Test patch version comparison"""
        result = VersionChecker.compare_versions('1.0.0', '1.0.1')
        assert result == 'patch'
    
    def test_compare_versions_minor(self):
        """Test minor version comparison"""
        result = VersionChecker.compare_versions('1.0.0', '1.1.0')
        assert result == 'minor'
    
    def test_compare_versions_major(self):
        """Test major version comparison"""
        result = VersionChecker.compare_versions('1.0.0', '2.0.0')
        assert result == 'major'
    
    def test_compare_versions_no_update(self):
        """Test when there's no update"""
        result = VersionChecker.compare_versions('1.1.0', '1.0.0')
        assert result is None
    
    def test_is_newer(self):
        """Test is_newer function"""
        assert VersionChecker.is_newer('2.0.0', '1.0.0') is True
        assert VersionChecker.is_newer('1.0.0', '2.0.0') is False
    
    def test_normalize_version(self):
        """Test version normalization"""
        assert VersionChecker.normalize_version('v1.0.0') == '1.0.0'
        assert VersionChecker.normalize_version('1.0.0') == '1.0.0'

class TestGitHubService:
    """Tests for GitHubService"""
    
    def test_parse_repo_url(self):
        """Test GitHub URL parsing"""
        service = GitHubService()
        
        owner, repo = service.parse_repo_url('https://github.com/python/cpython')
        assert owner == 'python'
        assert repo == 'cpython'
        
        owner, repo = service.parse_repo_url('https://github.com/python/cpython.git')
        assert owner == 'python'
        assert repo == 'cpython'
    
    def test_parse_invalid_url(self):
        """Test parsing invalid URL"""
        service = GitHubService()
        owner, repo = service.parse_repo_url('invalid-url')
        assert owner is None
        assert repo is None
        assert VersionChecker.is_newer('2.0.0', '1.0.0') is True
        assert VersionChecker.is_newer('1.0.0', '2.0.0') is False
    
    def test_normalize_version(self):
        """Test version normalization"""
        result = VersionChecker.normalize_version('v1.0.0')
        assert result == '1.0.0'
