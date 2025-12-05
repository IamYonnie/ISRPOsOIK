# MIT License

from datetime import datetime
from typing import Optional, Dict
import logging
from packaging import version as pkg_version

logger = logging.getLogger(__name__)

class VersionChecker:
    """Service for version comparison and update detection"""
    
    @staticmethod
    def compare_versions(old_version: str, new_version: str) -> Optional[str]:
        """
        Compare two versions and return update type
        
        Returns: 'major', 'minor', 'patch', or None if versions cannot be compared
        """
        try:
            old = pkg_version.parse(old_version)
            new = pkg_version.parse(new_version)
            
            if new <= old:
                return None  # Not an update
            
            # For PEP440 versions
            if hasattr(old, 'major') and hasattr(new, 'major'):
                if new.major > old.major:
                    return 'major'
                elif new.minor > old.minor:
                    return 'minor'
                else:
                    return 'patch'
            
            # Fallback for simple comparison
            return 'patch'
        except Exception as e:
            logger.warning(f'Error comparing versions {old_version} and {new_version}: {e}')
            return None
    
    @staticmethod
    def is_newer(version1: str, version2: str) -> bool:
        """Check if version1 is newer than version2"""
        try:
            return pkg_version.parse(version1) > pkg_version.parse(version2)
        except Exception as e:
            logger.warning(f'Error comparing versions: {e}')
            return False
    
    @staticmethod
    def normalize_version(version_str: str) -> str:
        """Normalize version string"""
        try:
            # Remove 'v' prefix if present
            if version_str.startswith('v'):
                version_str = version_str[1:]
            return str(pkg_version.parse(version_str))
        except Exception:
            return version_str
