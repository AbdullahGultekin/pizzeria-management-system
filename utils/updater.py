"""
Auto-update mechanisme voor de Pizzeria Management System.

Dit module controleert op updates en kan automatisch nieuwe versies downloaden.
"""
import json
import os
import sys
import platform
import threading
from typing import Optional, Dict, Any
from pathlib import Path
import requests
from logging_config import get_logger

logger = get_logger("pizzeria.updater")

# GitHub repository info
GITHUB_REPO = "AbdullahGultekin/pizzeria-management-system"
GITHUB_API_BASE = "https://api.github.com/repos"
RELEASES_URL = f"{GITHUB_API_BASE}/{GITHUB_REPO}/releases/latest"


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
            response = requests.get(RELEASES_URL, timeout=timeout)
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

