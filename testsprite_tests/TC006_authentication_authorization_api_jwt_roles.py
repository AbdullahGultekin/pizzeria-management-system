import requests
from requests.exceptions import RequestException, Timeout

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_authentication_authorization_api_jwt_roles():
    """
    Verify JWT-based authentication and role-based access control for Admin, Kassa,
    and Public users, ensuring secure login and restricted access to protected endpoints.
    """
    login_url = f"{BASE_URL}/api/v1/auth/login"
    protected_url = f"{BASE_URL}/api/v1/reports/daily"  # Admin only endpoint
    kassa_protected_url = f"{BASE_URL}/api/v1/orders"  # Kassa can access orders
    public_protected_url = f"{BASE_URL}/api/v1/menu/public"  # Public accessible endpoint

    # Credentials for different roles (these should exist in the system)
    users = {
        "admin": {"username": "admin", "password": "admin123"},
        "kassa": {"username": "kassa", "password": "kassa123"},
        "invalid": {"username": "invalid_user", "password": "wrong_pass"},
    }

    tokens = {}

    # Helper function to login and get JWT token
    def login(user):
        try:
            resp = requests.post(
                login_url,
                data={"username": user["username"], "password": user["password"]},  # Use form-data, not JSON
                timeout=TIMEOUT,
            )
            return resp
        except (RequestException, Timeout) as e:
            assert False, f"Login request failed: {e}"

    # 1. Test login success for Admin and Kassa users
    for role in ["admin", "kassa"]:
        response = login(users[role])
        assert response.status_code == 200, f"{role} login failed with status {response.status_code}"
        json_data = response.json()
        assert "access_token" in json_data, f"{role} login response missing access_token"
        tokens[role] = json_data["access_token"]
        # Optionally verify token format (JWT tokens contain '.')
        assert '.' in tokens[role], f"{role} token is not a valid JWT"

    # 2. Test public endpoint access without authentication
    public_resp = requests.get(public_protected_url, timeout=TIMEOUT)
    assert public_resp.status_code == 200, f"Public endpoint should be accessible without auth, got {public_resp.status_code}"

    # 3. Test login failure for invalid credentials
    invalid_response = login(users["invalid"])
    assert invalid_response.status_code == 401, \
        f"Invalid login should return 401 Unauthorized, got {invalid_response.status_code}"

    # 4. Test access to admin protected endpoint
    # Admin user should have access
    resp_admin = requests.get(
        protected_url,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
        timeout=TIMEOUT,
    )
    assert resp_admin.status_code == 200, f"Admin should access admin endpoint, got {resp_admin.status_code}"

    # Kassa user should NOT have access to admin endpoint
    resp_kassa_admin = requests.get(
        protected_url,
        headers={"Authorization": f"Bearer {tokens['kassa']}"},
        timeout=TIMEOUT,
    )
    assert resp_kassa_admin.status_code in [401, 403], f"Kassa should NOT access admin endpoint, got {resp_kassa_admin.status_code}"

    # 5. Test access to Kassa protected endpoint
    # Kassa user should have access
    resp_kassa = requests.get(
        kassa_protected_url,
        headers={"Authorization": f"Bearer {tokens['kassa']}"},
        timeout=TIMEOUT,
    )
    assert resp_kassa.status_code == 200, f"Kassa user should access kassa endpoint, got {resp_kassa.status_code}"

    # Admin user should have access to Kassa endpoint (assuming admin has all rights)
    resp_admin_kassa = requests.get(
        kassa_protected_url,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
        timeout=TIMEOUT,
    )
    assert resp_admin_kassa.status_code == 200, f"Admin should access kassa endpoint, got {resp_admin_kassa.status_code}"

    # 6. Test public endpoint with authenticated users
    # With admin token
    resp_public_admin = requests.get(
        public_protected_url,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
        timeout=TIMEOUT,
    )
    assert resp_public_admin.status_code == 200, f"Admin should access public endpoint, got {resp_public_admin.status_code}"

    # With kassa token
    resp_public_kassa = requests.get(
        public_protected_url,
        headers={"Authorization": f"Bearer {tokens['kassa']}"},
        timeout=TIMEOUT,
    )
    assert resp_public_kassa.status_code == 200, f"Kassa should access public endpoint, got {resp_public_kassa.status_code}"

    # 7. Access protected endpoints without token - should fail
    resp_no_token_admin = requests.get(protected_url, timeout=TIMEOUT)
    assert resp_no_token_admin.status_code in [401, 403], f"Access without token to admin endpoint should be denied, got {resp_no_token_admin.status_code}"

    resp_no_token_kassa = requests.get(kassa_protected_url, timeout=TIMEOUT)
    assert resp_no_token_kassa.status_code in [401, 403], f"Access without token to kassa endpoint should be denied, got {resp_no_token_kassa.status_code}"

    print("✅ All authentication and authorization tests passed!")

test_authentication_authorization_api_jwt_roles()
