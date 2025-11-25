import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}


def create_menu_item():
    payload = {
        "name": "Test Pizza",
        "description": "Sample pizza for testing",
        "price": 8.00,
        "available": True,
        "category": "Pizza",
        "options": [
            {
                "name": "Size",
                "choices": [
                    {"name": "Small", "price": 0},
                    {"name": "Medium", "price": 2},
                    {"name": "Large", "price": 4}
                ]
            },
            {
                "name": "Extra Cheese",
                "choices": [
                    {"name": "Yes", "price": 1},
                    {"name": "No", "price": 0}
                ]
            }
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/menu/items",
        json=payload,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()  # Expecting a dict with item details including 'id'


def delete_menu_item(item_id):
    response = requests.delete(
        f"{BASE_URL}/api/menu/items/{item_id}",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    # Accept 204 No Content or 200 OK on deletion
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to delete menu item {item_id}, status code: {response.status_code}")


def create_cart():
    response = requests.post(
        f"{BASE_URL}/api/shopping_cart",
        json={},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()  # Expecting a dict with cart info including 'id'


def delete_cart(cart_id):
    response = requests.delete(
        f"{BASE_URL}/api/shopping_cart/{cart_id}",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to delete shopping cart {cart_id}, status code: {response.status_code}")


def test_shopping_cart_api_quantity_and_options():
    # Create menu item to add to cart
    menu_item = None
    cart = None
    try:
        menu_item = create_menu_item()
        menu_item_id = menu_item.get("id")
        assert menu_item_id, "Menu item ID should be present after creation"

        # Create shopping cart
        cart = create_cart()
        cart_id = cart.get("id")
        assert cart_id, "Cart ID should be present after creation"

        # Add product with options and quantity=1 to the cart
        add_payload = {
            "product_id": menu_item_id,
            "quantity": 1,
            "options": {
                "Size": "Medium",
                "Extra Cheese": "Yes"
            }
        }
        add_response = requests.post(
            f"{BASE_URL}/api/shopping_cart/{cart_id}/items",
            json=add_payload,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert add_response.status_code == 201, f"Expected 201 Created, got {add_response.status_code}"
        item_data = add_response.json()
        item_id = item_data.get("id")
        assert item_id, "Cart item ID should be returned after adding item"

        # Get cart details to verify options and price calculation
        get_cart_response = requests.get(
            f"{BASE_URL}/api/shopping_cart/{cart_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert get_cart_response.status_code == 200, f"Expected 200 OK for get cart, got {get_cart_response.status_code}"
        cart_data = get_cart_response.json()

        # Validate product options presence and correctness in the cart
        items = cart_data.get("items", [])
        assert len(items) == 1, "Cart should contain exactly one item"
        cart_item = items[0]
        assert cart_item.get("product_id") == menu_item_id, "Product ID in cart item should match added product"

        options = cart_item.get("options", {})
        assert options.get("Size") == "Medium", "Product option 'Size' should be 'Medium'"
        assert options.get("Extra Cheese") == "Yes", "Product option 'Extra Cheese' should be 'Yes'"

        # Validate quantity is 1 initially
        assert cart_item.get("quantity") == 1, "Initial quantity should be 1"

        # Validate total price calculation is correct
        base_price = menu_item.get("price", 0)
        # Option prices from menu item definition
        size_price = 2  # Medium size additional price
        cheese_price = 1  # Extra cheese additional price
        expected_price = (base_price + size_price + cheese_price) * 1
        assert abs(cart_item.get("total_price", 0) - expected_price) < 0.01, "Total price calculation mismatch for quantity=1"

        # Change quantity to 3
        update_payload = {
            "quantity": 3
        }
        update_response = requests.put(
            f"{BASE_URL}/api/shopping_cart/{cart_id}/items/{item_id}",
            json=update_payload,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert update_response.status_code == 200, f"Expected 200 OK on quantity update, got {update_response.status_code}"
        updated_item = update_response.json()
        assert updated_item.get("quantity") == 3, "Quantity should be updated to 3"

        # Get cart details again after quantity update
        get_cart_response_2 = requests.get(
            f"{BASE_URL}/api/shopping_cart/{cart_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert get_cart_response_2.status_code == 200, "Expected 200 OK for get cart after quantity update"
        cart_data_2 = get_cart_response_2.json()
        items_2 = cart_data_2.get("items", [])
        assert len(items_2) == 1, "Cart should still have one item after quantity update"
        cart_item_2 = items_2[0]

        # Confirm total price reflects quantity 3
        expected_price_quantity_3 = (base_price + size_price + cheese_price) * 3
        assert abs(cart_item_2.get("total_price", 0) - expected_price_quantity_3) < 0.01, "Total price calculation mismatch for quantity=3"

        # Confirm options remain unchanged
        options_2 = cart_item_2.get("options", {})
        assert options_2.get("Size") == "Medium", "Product option 'Size' should remain 'Medium' after quantity update"
        assert options_2.get("Extra Cheese") == "Yes", "Product option 'Extra Cheese' should remain 'Yes' after quantity update"

    finally:
        # Cleanup created resources
        if cart and "id" in cart:
            try:
                delete_cart(cart["id"])
            except Exception:
                pass
        if menu_item and "id" in menu_item:
            try:
                delete_menu_item(menu_item["id"])
            except Exception:
                pass


test_shopping_cart_api_quantity_and_options()
