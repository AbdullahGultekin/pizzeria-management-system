"""
Auto-update mechanisme voor de Pizzeria Management System.

Dit module controleert op updates en kan automatisch nieuwe versies downloaden.
Ondersteunt zowel exe downloads als automatische git pull updates.
"""
import json
import os
import sys
import platform
import threading
import subprocess
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import requests
from logging_config import get_logger
from config import load_settings

logger = get_logger("pizzeria.updater")

# GitHub repository info - can be overridden in settings.json
GITHUB_API_BASE = "https://api.github.com/repos"

def get_github_repo() -> str:
    """
    Get GitHub repository name from settings or use default.
    
    Returns:
        Repository name in format "owner/repo"
    """
    settings = load_settings()
    return settings.get("github_repo", "AbdullahGultekin/pizzeria-management-system")

def get_releases_url() -> str:
    """
    Get GitHub releases API URL.
    
    Returns:
        Full URL to latest releases endpoint
    """
    repo = get_github_repo()
    return f"{GITHUB_API_BASE}/{repo}/releases/latest"


class UpdateChecker:
    """Check for application updates from GitHub releases."""
    
    def __init__(self, current_version: str):
        """
        Initialize update checker.
        
        Args:
            current_version: Current application version (e.g., "1.0.0")
        """
        self.current_version = current_version
        self.latest_version: Optional[str] = None
        self.latest_release: Optional[Dict[str, Any]] = None
        self.download_url: Optional[str] = None
    
    def check_for_updates(self, timeout: int = 5) -> bool:
        """
        Check for available updates.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            True if update is available, False otherwise
        """
        try:
            repo = get_github_repo()
            releases_url = get_releases_url()
            response = requests.get(releases_url, timeout=timeout)
            
            # Handle 404 specifically - repository not found or no releases
            if response.status_code == 404:
                logger.debug(f"Repository or releases not found: {repo} (404). "
                           f"Check if repository exists, is public, and has published releases. "
                           f"URL: {releases_url}")
                return False
            
            # Handle 403 - repository is private or requires authentication
            if response.status_code == 403:
                logger.debug(f"Repository access denied (403): {repo}. "
                           f"Repository may be private or rate limit exceeded. "
                           f"URL: {releases_url}")
                return False
            
            response.raise_for_status()
            
            release_data = response.json()
            self.latest_version = release_data.get("tag_name", "").lstrip("v")
            self.latest_release = release_data
            
            # Find download URL for current platform
            self.download_url = self._find_download_url(release_data.get("assets", []))
            
            # Compare versions
            if self._is_newer_version(self.latest_version, self.current_version):
                logger.info(f"Update available: {self.current_version} -> {self.latest_version}")
                return True
            else:
                logger.debug(f"No update available. Current: {self.current_version}, Latest: {self.latest_version}")
                return False
                
        except requests.exceptions.RequestException as e:
            # Only log warning for non-404 errors (network issues, etc.)
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                logger.debug("No releases found or repository not available")
            else:
                logger.warning(f"Could not check for updates: {e}")
            return False
        except Exception as e:
            logger.exception(f"Error checking for updates: {e}")
            return False
    
    def _find_download_url(self, assets: list) -> Optional[str]:
        """
        Find download URL for current platform.
        
        Args:
            assets: List of release assets
            
        Returns:
            Download URL or None
        """
        system = platform.system()
        
        # Look for platform-specific asset
        for asset in assets:
            name = asset.get("name", "").lower()
            browser_download_url = asset.get("browser_download_url", "")
            
            if system == "Windows":
                if name.endswith(".exe"):
                    return browser_download_url
            elif system == "Darwin":  # macOS
                if name.endswith(".dmg") or name.endswith(".app"):
                    return browser_download_url
            elif system == "Linux":
                if name.endswith(".AppImage") or name.endswith(".deb"):
                    return browser_download_url
        
        # Fallback: return first asset
        if assets:
            return assets[0].get("browser_download_url")
        
        return None
    
    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """
        Compare two version strings.
        
        Args:
            version1: Version to check (e.g., "1.1.0")
            version2: Current version (e.g., "1.0.0")
            
        Returns:
            True if version1 is newer than version2
        """
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]
            
            # Pad to same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            return v1_parts > v2_parts
        except (ValueError, AttributeError):
            # If version format is invalid, assume no update
            return False
    
    def get_update_info(self) -> Dict[str, Any]:
        """
        Get information about available update.
        
        Returns:
            Dictionary with update information
        """
        if not self.latest_release:
            return {}
        
        return {
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "download_url": self.download_url,
            "release_notes": self.latest_release.get("body", ""),
            "published_at": self.latest_release.get("published_at", ""),
            "release_url": self.latest_release.get("html_url", "")
        }


def check_for_updates_async(current_version: str, callback=None):
    """
    Check for updates in background thread.
    
    Args:
        current_version: Current application version
        callback: Optional callback function to call with update info
    """
    def worker():
        checker = UpdateChecker(current_version)
        has_update = checker.check_for_updates()
        
        if callback and has_update:
            update_info = checker.get_update_info()
            callback(update_info)
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def is_git_repository() -> bool:
    """
    Check if current directory is a git repository.
    
    Returns:
        True if git repository, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            timeout=2,
            cwd=Path.cwd()
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def perform_git_update(backup_data: bool = True) -> Tuple[bool, str]:
    """
    Perform automatic update via git pull.
    
    Args:
        backup_data: Whether to backup local data files before update
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not is_git_repository():
        return False, "Geen git repository gevonden. Automatische update niet mogelijk."
    
    try:
        project_root = Path.cwd()
        backup_dir = project_root / "data" / "backup" / "auto_update"
        
        # Backup local data if requested
        if backup_data:
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
                local_files = ["pizzeria.db", "settings.json"]
                for file in local_files:
                    src = project_root / file
                    if src.exists():
                        dst = backup_dir / file
                        import shutil
                        shutil.copy2(src, dst)
                logger.info("Local data backed up before update")
            except Exception as e:
                logger.warning(f"Could not backup data: {e}")
        
        # Stash local changes
        try:
            subprocess.run(
                ["git", "stash", "push", "-m", "Auto-stash before update"],
                check=False,
                capture_output=True,
                timeout=10,
                cwd=project_root
            )
        except Exception as e:
            logger.debug(f"Could not stash changes: {e}")
        
        # Pull latest changes
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Git update successful: {output}")
            return True, f"Update succesvol!\n\n{output}"
        else:
            error = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Git update failed: {error}")
            return False, f"Update gefaald:\n\n{error}"
            
    except subprocess.TimeoutExpired:
        return False, "Update timeout. Probeer het later opnieuw."
    except FileNotFoundError:
        return False, "Git niet gevonden. Installeer Git om automatische updates te gebruiken."
    except Exception as e:
        logger.exception(f"Error during git update: {e}")
        return False, f"Fout tijdens update: {str(e)}"

