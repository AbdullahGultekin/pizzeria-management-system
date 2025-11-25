"""Helper functions for TestSprite tests."""
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_auth_token(username="admin", password="admin123"):
    """Get JWT token for authentication."""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": username, "password": password},  # Use form-data for OAuth2
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_headers(token=None):
    """Get headers with authentication."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


