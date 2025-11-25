import requests
import time

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30

def test_order_management_api_status_workflow():
    # Status workflow sequence as per requirements
    status_sequence = [
        "Nieuw",           # New
        "In behandeling",  # In progress
        "Klaar",           # Ready
        "Onderweg",        # On the way
        "Afgeleverd",      # Delivered
        "Geannuleerd"      # Cancelled
    ]
    
    created_order_id = None

    try:
        # Step 1: Create a new order
        new_order_payload = {
            "customer": {
                "name": "Test Customer",
                "phone": "0612345678",
                "address": "Teststraat 1, Teststad"
            },
            "items": [
                {
                    "product_id": 1,        # Assuming product_id 1 exists
                    "quantity": 2,
                    "options": []
                }
            ],
            "payment_method": "cash",
            "notes": "Test order for status workflow"
        }
        create_resp = requests.post(
            f"{BASE_URL}/orders",
            headers=HEADERS,
            json=new_order_payload,
            timeout=TIMEOUT
        )
        assert create_resp.status_code == 201, f"Order creation failed: {create_resp.text}"
        created_order = create_resp.json()
        created_order_id = created_order.get("id")
        assert created_order_id is not None, "Created order ID missing"
        assert created_order.get("status") == "Nieuw", f"Initial order status not 'Nieuw', got {created_order.get('status')}"

        # Step 2: Update order status through the workflow except the last (Geannuleerd)
        for status in status_sequence[1:-1]:
            update_payload = {"status": status}
            update_resp = requests.put(
                f"{BASE_URL}/orders/{created_order_id}/status",
                headers=HEADERS,
                json=update_payload,
                timeout=TIMEOUT
            )
            assert update_resp.status_code == 200, f"Failed to update status to {status}: {update_resp.text}"
            updated_order = update_resp.json()
            assert updated_order.get("status") == status, f"Order status not updated to {status}, got {updated_order.get('status')}"

            # Optionally verify current order via GET
            get_resp = requests.get(
                f"{BASE_URL}/orders/{created_order_id}",
                headers=HEADERS,
                timeout=TIMEOUT
            )
            assert get_resp.status_code == 200, f"Failed to get order after status update to {status}"
            current_order = get_resp.json()
            assert current_order.get("status") == status, f"GET order status mismatch: expected {status}, got {current_order.get('status')}"

        # Step 3: Test cancel status separately (Geannuleerd)
        cancel_payload = {"status": "Geannuleerd"}
        cancel_resp = requests.put(
            f"{BASE_URL}/orders/{created_order_id}/status",
            headers=HEADERS,
            json=cancel_payload,
            timeout=TIMEOUT
        )
        # Depending on business rules, cancelling might be allowed anytime or only if not delivered.
        # Test expects it can be set.
        assert cancel_resp.status_code == 200, f"Failed to update status to Geannuleerd: {cancel_resp.text}"
        cancelled_order = cancel_resp.json()
        assert cancelled_order.get("status") == "Geannuleerd", f"Order status not updated to Geannuleerd, got {cancelled_order.get('status')}"

        # Step 4: Test real-time tracking endpoint(s)
        # Usually real-time tracking is via websocket, but try GET order tracking/status endpoint as fallback
        tracking_resp = requests.get(
            f"{BASE_URL}/orders/{created_order_id}/tracking",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        # If endpoint exists, check response is 200 and contains statuses or tracking info
        if tracking_resp.status_code == 200:
            tracking_data = tracking_resp.json()
            assert "status" in tracking_data, "Tracking data missing 'status'"
            assert isinstance(tracking_data["status"], str), "Tracking status should be a string"

    finally:
        # Cleanup: delete the created order
        if created_order_id is not None:
            try:
                del_resp = requests.delete(
                    f"{BASE_URL}/orders/{created_order_id}",
                    headers=HEADERS,
                    timeout=TIMEOUT
                )
                # Accept 200 or 204 as successful delete
                assert del_resp.status_code in [200, 204], f"Failed to delete order id {created_order_id}"
            except Exception:
                pass  # Ignore delete failures in cleanup

test_order_management_api_status_workflow()
