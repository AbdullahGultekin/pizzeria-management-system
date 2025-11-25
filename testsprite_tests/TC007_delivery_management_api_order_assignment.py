import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_delivery_management_api_order_assignment():
    # Helper functions
    def create_customer():
        customer_data = {
            "name": "Test Customer",
            "phone": "+310612345678",
            "email": "testcustomer@example.com",
            "address": "Teststraat 1, 1234AB Amsterdam"
        }
        resp = requests.post(f"{BASE_URL}/api/customers", json=customer_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["id"]

    def create_menu_item():
        menu_data = {
            "name": "Test Pizza",
            "description": "Delicious test pizza",
            "price": 9.99,
            "category": "Pizza",
            "available": True
        }
        resp = requests.post(f"{BASE_URL}/api/menu/items", json=menu_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["id"]

    def create_order(customer_id, menu_item_id):
        order_data = {
            "customer_id": customer_id,
            "items": [
                {
                    "menu_item_id": menu_item_id,
                    "quantity": 1,
                    "options": []
                }
            ]
        }
        resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["id"]

    def create_courier():
        courier_data = {
            "name": "Test Courier",
            "phone": "+310698765432"
        }
        resp = requests.post(f"{BASE_URL}/api/couriers", json=courier_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["id"]

    def assign_order_to_courier(order_id, courier_id):
        assign_data = {"courier_id": courier_id}
        resp = requests.put(f"{BASE_URL}/api/deliveries/{order_id}/assign", json=assign_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp

    def update_delivery_status(order_id, status):
        status_data = {"status": status}
        resp = requests.put(f"{BASE_URL}/api/deliveries/{order_id}/status", json=status_data, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp

    def get_courier_performance(courier_id):
        resp = requests.get(f"{BASE_URL}/api/couriers/{courier_id}/performance", headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp

    # Test execution with resource cleanup
    customer_id = None
    menu_item_id = None
    order_id = None
    courier_id = None

    try:
        # Setup resources
        customer_id = create_customer()
        menu_item_id = create_menu_item()
        order_id = create_order(customer_id, menu_item_id)
        courier_id = create_courier()

        # Assign order to courier
        resp_assign = assign_order_to_courier(order_id, courier_id)
        assign_resp_json = resp_assign.json()
        assert resp_assign.status_code == 200
        assert "assigned" in assign_resp_json and assign_resp_json["assigned"] is True

        # Update delivery status stepwise and verify
        for status in ["In behandeling", "Onderweg", "Afgeleverd"]:
            resp_status = update_delivery_status(order_id, status)
            status_resp_json = resp_status.json()
            assert resp_status.status_code == 200
            assert status_resp_json.get("status") == status

        # Retrieve courier performance data
        resp_perf = get_courier_performance(courier_id)
        perf_data = resp_perf.json()
        assert resp_perf.status_code == 200
        assert isinstance(perf_data, dict)
        assert "total_deliveries" in perf_data
        assert "successful_deliveries" in perf_data

    finally:
        # Cleanup orders, couriers, menu items, customers
        if order_id:
            try:
                requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass
        if courier_id:
            try:
                requests.delete(f"{BASE_URL}/api/couriers/{courier_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass
        if menu_item_id:
            try:
                requests.delete(f"{BASE_URL}/api/menu/items/{menu_item_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass
        if customer_id:
            try:
                requests.delete(f"{BASE_URL}/api/customers/{customer_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass

test_delivery_management_api_order_assignment()
