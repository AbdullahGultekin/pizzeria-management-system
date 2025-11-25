import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {
    "Content-Type": "application/json"
}


def test_customer_management_api_functionality():
    # Customer data for creation
    new_customer_data = {
        "first_name": "Jan",
        "last_name": "de Vries",
        "email": "jan.devries@example.com",
        "phone_number": "0612345678",
        "address": {
            "street": "Dorpsstraat 1",
            "city": "Amsterdam",
            "postal_code": "1011AA",
            "country": "NL"
        }
    }

    created_customer_id = None

    try:
        # 1. Create a new customer
        create_resp = requests.post(
            f"{BASE_URL}/api/customers/",
            json=new_customer_data,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert create_resp.status_code == 201, f"Expected 201 Created, got {create_resp.status_code}"
        created_customer = create_resp.json()
        assert "id" in created_customer, "Response missing customer ID"
        created_customer_id = created_customer["id"]

        # Validate returned fields match input for key fields
        for field in ["first_name", "last_name", "email", "phone_number"]:
            assert created_customer[field] == new_customer_data[field], f"Mismatch in field {field}"
        for addr_field in ["street", "city", "postal_code", "country"]:
            assert created_customer["address"][addr_field] == new_customer_data["address"][addr_field], f"Address field {addr_field} mismatch"

        # 2. Search customer by phone number
        search_resp = requests.get(
            f"{BASE_URL}/api/customers/search/",
            params={"phone": new_customer_data["phone_number"]},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert search_resp.status_code == 200, f"Expected 200 OK for search, got {search_resp.status_code}"
        customers_found = search_resp.json()
        assert isinstance(customers_found, list), "Search response is not a list"
        assert any(c["id"] == created_customer_id for c in customers_found), "Created customer not found in search results"

        # 3. Update customer details
        updated_data = {
            "first_name": "Jan Pieter",
            "email": "jan.pieter.devries@example.com",
            "address": {
                "street": "Nieuwstraat 2",
                "city": "Amsterdam",
                "postal_code": "1011BB",
                "country": "NL"
            }
        }

        update_resp = requests.put(
            f"{BASE_URL}/api/customers/{created_customer_id}/",
            json=updated_data,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert update_resp.status_code == 200, f"Expected 200 OK on update, got {update_resp.status_code}"
        updated_customer = update_resp.json()

        # Validate updated fields
        assert updated_customer["first_name"] == updated_data["first_name"], "First name not updated correctly"
        assert updated_customer["email"] == updated_data["email"], "Email not updated correctly"
        for addr_field in ["street", "city", "postal_code", "country"]:
            assert updated_customer["address"][addr_field] == updated_data["address"][addr_field], f"Address field {addr_field} not updated"

        # 4. Retrieve customer information by ID
        get_resp = requests.get(
            f"{BASE_URL}/api/customers/{created_customer_id}/",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert get_resp.status_code == 200, f"Expected 200 OK on get, got {get_resp.status_code}"
        retrieved_customer = get_resp.json()

        # Validate all data matches updated data
        assert retrieved_customer["id"] == created_customer_id, "Customer ID mismatch on retrieval"
        assert retrieved_customer["first_name"] == updated_data["first_name"], "First name mismatch on retrieval"
        assert retrieved_customer["email"] == updated_data["email"], "Email mismatch on retrieval"
        for addr_field in ["street", "city", "postal_code", "country"]:
            assert retrieved_customer["address"][addr_field] == updated_data["address"][addr_field], f"Address field {addr_field} mismatch on retrieval"

    finally:
        # Cleanup: delete the created customer if exists
        if created_customer_id:
            try:
                del_resp = requests.delete(
                    f"{BASE_URL}/api/customers/{created_customer_id}/",
                    headers=HEADERS,
                    timeout=TIMEOUT,
                )
                # Accept 200 OK or 204 No Content as successful deletion
                assert del_resp.status_code in (200, 204), f"Failed to delete customer, status {del_resp.status_code}"
            except Exception:
                # Suppress exceptions on cleanup to not mask test results
                pass


test_customer_management_api_functionality()
