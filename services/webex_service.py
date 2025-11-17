"""
Webex Calling Integration Service

Monitors incoming calls via Webex API and provides call information
for automatic phone number filling in the application.
"""

import requests
import threading
import time
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime, timedelta
from logging_config import get_logger
from config import load_settings, save_settings

logger = get_logger("pizzeria.services.webex")


class WebexCallMonitor:
    """
    Service for monitoring Webex calls and extracting caller information.
    
    This service polls the Webex API periodically to detect incoming calls
    and provides call information to the application.
    """
    
    # Webex API endpoints
    TOKEN_URL = "https://webexapis.com/v1/access_token"
    CALLS_URL = "https://webexapis.com/v1/telephony/calls"
    PEOPLE_URL = "https://webexapis.com/v1/people"
    
    def __init__(self):
        """Initialize Webex call monitor."""
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.monitoring: bool = False
        self.poll_interval: int = 2  # Poll every 2 seconds
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_call_id: Optional[str] = None
        self.on_incoming_call: Optional[Callable[[str, Optional[str]]]] = None
        
        # Load credentials from settings
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load Webex credentials from settings."""
        settings = load_settings()
        self.client_id = settings.get("webex_client_id", "")
        self.client_secret = settings.get("webex_client_secret", "")
        self.access_token = settings.get("webex_access_token")
        self.refresh_token = settings.get("webex_refresh_token")
        
        # Check if token is expired
        token_expires = settings.get("webex_token_expires_at")
        if token_expires:
            try:
                expires_at = datetime.fromisoformat(token_expires)
                if expires_at < datetime.now():
                    logger.info("Webex access token expired, refresh needed")
                    self.access_token = None
            except (ValueError, TypeError):
                pass
    
    def _save_credentials(self) -> None:
        """Save Webex credentials to settings."""
        settings = load_settings()
        settings["webex_client_id"] = self.client_id
        settings["webex_client_secret"] = self.client_secret
        if self.access_token:
            settings["webex_access_token"] = self.access_token
        if self.refresh_token:
            settings["webex_refresh_token"] = self.refresh_token
        if self.token_expires_at:
            settings["webex_token_expires_at"] = self.token_expires_at.isoformat()
        save_settings(settings)
    
    def set_credentials(self, client_id: str, client_secret: str) -> None:
        """
        Set Webex API credentials.
        
        Args:
            client_id: Webex client ID
            client_secret: Webex client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._save_credentials()
        logger.info("Webex credentials saved")
    
    def set_access_token(self, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 3600) -> None:
        """
        Set access token (after OAuth flow).
        
        Args:
            access_token: OAuth access token
            refresh_token: Optional refresh token
            expires_in: Token expiration time in seconds
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        self._save_credentials()
        logger.info("Webex access token saved")
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False
        
        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.set_access_token(
                    data.get("access_token"),
                    data.get("refresh_token", self.refresh_token),
                    data.get("expires_in", 3600)
                )
                logger.info("Webex access token refreshed")
                return True
            else:
                logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.exception(f"Error refreshing token: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _check_token_valid(self) -> bool:
        """Check if access token is valid."""
        if not self.access_token:
            return False
        if self.token_expires_at and self.token_expires_at < datetime.now():
            # Try to refresh
            if self._refresh_access_token():
                return True
            return False
        return True
    
    def get_active_calls(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of active calls from Webex API.
        
        Returns:
            List of active calls or None if error
        """
        if not self._check_token_valid():
            logger.warning("No valid access token for Webex API")
            return None
        
        try:
            headers = self._get_headers()
            response = requests.get(
                self.CALLS_URL,
                headers=headers,
                params={"state": "active"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                calls = data.get("items", [])
                return calls
            elif response.status_code == 401:
                # Token expired, try refresh
                logger.warning("Token expired, attempting refresh")
                if self._refresh_access_token():
                    return self.get_active_calls()  # Retry
                return None
            else:
                logger.error(f"Failed to get calls: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Error getting active calls: {e}")
            return None
    
    def extract_phone_number(self, call: Dict[str, Any]) -> Optional[str]:
        """
        Extract phone number from call data.
        
        Args:
            call: Call data from Webex API
            
        Returns:
            Phone number or None
        """
        # Try different fields where phone number might be
        # Webex API structure may vary
        phone_fields = [
            "from", "fromNumber", "callerId", "callerNumber",
            "remoteParty", "remotePartyNumber", "ani", "callingNumber"
        ]
        
        for field in phone_fields:
            value = call.get(field)
            if value:
                # Extract just the number (remove formatting)
                phone = str(value).strip()
                # Remove common formatting
                phone = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                # Remove country code if present (assume Belgium +32)
                if phone.startswith("32"):
                    phone = "0" + phone[2:]
                elif phone.startswith("0032"):
                    phone = "0" + phone[4:]
                # Return if looks like a phone number
                if phone and len(phone) >= 8 and phone.isdigit():
                    return phone
        
        return None
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        logger.info("Webex call monitor started")
        
        while self.monitoring:
            try:
                calls = self.get_active_calls()
                
                if calls:
                    # Find incoming calls
                    for call in calls:
                        call_id = call.get("id")
                        direction = call.get("direction", "").lower()
                        state = call.get("state", "").lower()
                        
                        # Check if this is a new incoming call
                        if (direction == "inbound" and 
                            state in ("ringing", "connected", "active") and
                            call_id != self.last_call_id):
                            
                            phone_number = self.extract_phone_number(call)
                            if phone_number:
                                logger.info(f"Incoming call detected: {phone_number}")
                                
                                # Get caller name if available
                                caller_name = call.get("callerName") or call.get("fromDisplayName")
                                
                                # Notify callback
                                if self.on_incoming_call:
                                    try:
                                        self.on_incoming_call(phone_number, caller_name)
                                    except Exception as e:
                                        logger.exception(f"Error in on_incoming_call callback: {e}")
                                
                                self.last_call_id = call_id
                
                # Sleep before next poll
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.exception(f"Error in monitor loop: {e}")
                time.sleep(self.poll_interval)
        
        logger.info("Webex call monitor stopped")
    
    def start_monitoring(self, on_incoming_call: Optional[Callable[[str, Optional[str]], None]] = None) -> bool:
        """
        Start monitoring for incoming calls.
        
        Args:
            on_incoming_call: Callback function(phone_number, caller_name) called when call detected
            
        Returns:
            True if monitoring started, False otherwise
        """
        if not self._check_token_valid():
            logger.error("Cannot start monitoring: no valid access token")
            return False
        
        if self.monitoring:
            logger.warning("Monitoring already running")
            return True
        
        self.on_incoming_call = on_incoming_call
        self.monitoring = True
        self.last_call_id = None
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="WebexCallMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("Webex call monitoring started")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop monitoring for incoming calls."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.monitor_thread = None
        logger.info("Webex call monitoring stopped")
    
    def is_configured(self) -> bool:
        """
        Check if Webex is properly configured.
        
        Returns:
            True if credentials and token are set
        """
        return bool(self.client_id and self.client_secret and self.access_token)
    
    def get_auth_url(self) -> str:
        """
        Get Webex OAuth authorization URL.
        
        Returns:
            Authorization URL
        """
        redirect_uri = "http://localhost:5000/callback"
        scopes = "vonk:oproepen_lezen vonk:mensen_lezen"
        
        return (
            f"https://webexapis.com/v1/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes.replace(' ', '%20')}"
            f"&state=webex_auth"
        )

