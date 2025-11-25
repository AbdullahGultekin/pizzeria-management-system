import requests
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Assuming authentication is required, provide valid credentials here
AUTH_TOKEN = None  # Replace with actual token if available

def get_auth_headers():
    headers = {
        "Content-Type": "application/json",
    }
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    return headers

def test_receipt_generation_api_format_and_print():
    # Step 1: Create a sample order resource to generate receipt from
    order_payload = {
        "customer": {
            "name": "Test Customer",
            "phone": "0612345678",
            "email": "test@example.com",
            "address": "Test Street 1, Amsterdam"
        },
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "options": [
                    {"option_id": 11, "price": 0.5},
                    {"option_id": 12, "price": 1.0}
                ]
            }
        ],
        "payment_method": "cash",
        "delivery": False
    }

    order_id = None
    try:
        create_order_resp = requests.post(f"{BASE_URL}/api/orders", headers=get_auth_headers(), json=order_payload, timeout=TIMEOUT)
        assert create_order_resp.status_code == 201, f"Failed to create order: {create_order_resp.text}"
        order_data = create_order_resp.json()
        order_id = order_data.get("id")
        assert order_id is not None, "Order ID not returned on creation."

        # Step 2: Request receipt generation for created order
        receipt_resp = requests.post(f"{BASE_URL}/api/receipt/generate", headers=get_auth_headers(), json={"order_id": order_id}, timeout=TIMEOUT)
        assert receipt_resp.status_code == 200, f"Receipt generation failed: {receipt_resp.text}"

        receipt_data = receipt_resp.json()
        # Validate receipt format keys
        assert "escpos_data" in receipt_data or "receipt_text" in receipt_data, "Receipt ESC/POS data or text not found in response."
        escpos_data = receipt_data.get("escpos_data")
        if escpos_data:
            # escpos_data should be a base64 or string representing ESC/POS command bytes, at least some data present
            assert isinstance(escpos_data, str) and len(escpos_data) > 0, "ESC/POS data is empty or invalid."

        # Validate QR code presence in receipt
        qr_code = receipt_data.get("qr_code")
        if qr_code:
            # qr_code presumably base64 PNG or similar string representation
            assert isinstance(qr_code, str) and len(qr_code) > 0, "QR code data is empty or invalid."

        # Optional: Validate print queue integration status if provided
        print_status = receipt_data.get("print_status")
        if print_status:
            assert print_status in ["queued", "printed", "error", "not_configured"], f"Invalid print_status value: {print_status}"

    finally:
        # Clean up: delete the created order if possible
        if order_id:
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=get_auth_headers(), timeout=TIMEOUT)
                assert del_resp.status_code in (200, 204), f"Failed to delete order {order_id}: {del_resp.text}"
            except Exception:
                pass

test_receipt_generation_api_format_and_print()