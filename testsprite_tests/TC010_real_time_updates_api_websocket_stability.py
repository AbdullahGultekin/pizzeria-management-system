import json
import threading
import time
import websocket
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/orders"
REQUEST_TIMEOUT = 30

# Credentials for authentication - adjust accordingly
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "adminpass"
}

def get_jwt_token():
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        token = response.json().get("access_token")
        assert token is not None, "JWT token not found in login response"
        return token
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate and get JWT token: {e}")

def create_order(token):
    headers = {"Authorization": f"Bearer {token}"}
    # Minimal valid order payload - adjust if needed for your API
    order_payload = {
        "customer_phone": "0612345678",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "options": []
            }
        ],
        "payment_method": "cash",
        "delivery": False
    }
    try:
        response = requests.post(f"{BASE_URL}/api/orders", json=order_payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        order_data = response.json()
        order_id = order_data.get("id")
        assert order_id is not None, "Order ID not found in create order response"
        return order_id
    except Exception as e:
        raise RuntimeError(f"Failed to create order: {e}")

def delete_order(order_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except Exception as e:
        # Log or ignore, as cleanup might fail without affecting test result
        pass

def real_time_updates_api_websocket_stability():
    token = get_jwt_token()
    order_id = None

    # Prepare authentication header for websocket connection (commonly sent as a query param or header)
    # Assume the WS endpoint accepts token as query param ?token=...
    ws_url_with_token = f"{WS_URL}?token={token}"

    # Event flags and storage for websocket messages
    messages_received = []
    error_occurred = [False]
    ws_opened = [False]

    def on_message(ws, message):
        try:
            data = json.loads(message)
            # We expect updates about orders, check for order_id and relevant fields
            if "order_id" in data and data["order_id"] == order_id:
                messages_received.append(data)
        except Exception:
            pass  # ignore malformed messages

    def on_error(ws, error):
        error_occurred[0] = True

    def on_close(ws, close_status_code, close_msg):
        ws_opened[0] = False

    def on_open(ws):
        ws_opened[0] = True

    try:
        # Create order to receive websocket updates for
        order_id = create_order(token)
        headers = {"Authorization": f"Bearer {token}"}

        # Start websocket client in thread
        ws = websocket.WebSocketApp(ws_url_with_token,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        ws_thread = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 10, "ping_timeout": 5})
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for websocket to open or timeout
        timeout_sec = 10
        start_time = time.time()
        while not ws_opened[0] and time.time() - start_time < timeout_sec:
            time.sleep(0.1)
        assert ws_opened[0], "WebSocket connection failed to open."

        # Update order status through workflow to trigger updates
        statuses = ["In behandeling", "Klaar", "Onderweg", "Afgeleverd"]

        for status in statuses:
            update_payload = {"status": status}
            resp = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", json=update_payload, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            time.sleep(1)  # wait a bit for websocket to receive update

        # Wait a bit more for any remaining messages
        time.sleep(3)

        # Validate websocket stability/no errors
        assert not error_occurred[0], "Error occurred in WebSocket connection."

        # Validate at least one update per status received in websocket messages
        received_statuses = set()
        for msg in messages_received:
            st = msg.get("status")
            if st:
                received_statuses.add(st)
        for expected_status in statuses:
            assert expected_status in received_statuses, f"Status '{expected_status}' update not received in real-time updates."

    finally:
        # Cleanup: close websocket and delete order
        try:
            ws.close()
        except Exception:
            pass
        if order_id:
            delete_order(order_id, token)

real_time_updates_api_websocket_stability()