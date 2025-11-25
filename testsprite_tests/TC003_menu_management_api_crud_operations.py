import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def menu_management_api_crud_operations():
    headers = {"Content-Type": "application/json"}
    created_resources = {"category_id": None, "menu_item_id": None, "product_option_id": None}

    # Helper function to delete created resources
    def cleanup():
        if created_resources["product_option_id"]:
            try:
                resp = requests.delete(
                    f"{BASE_URL}/menu/product-options/{created_resources['product_option_id']}",
                    headers=headers,
                    timeout=TIMEOUT,
                )
                assert resp.status_code == 204
            except Exception:
                pass
        if created_resources["menu_item_id"]:
            try:
                resp = requests.delete(
                    f"{BASE_URL}/menu/items/{created_resources['menu_item_id']}",
                    headers=headers,
                    timeout=TIMEOUT,
                )
                assert resp.status_code == 204
            except Exception:
                pass
        if created_resources["category_id"]:
            try:
                resp = requests.delete(
                    f"{BASE_URL}/menu/categories/{created_resources['category_id']}",
                    headers=headers,
                    timeout=TIMEOUT,
                )
                assert resp.status_code == 204
            except Exception:
                pass

    try:
        # 1. Create a category
        category_payload = {
            "name": f"Test Category {uuid.uuid4()}",
            "description": "Category for testing CRUD operations"
        }
        response = requests.post(f"{BASE_URL}/menu/categories", json=category_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201
        category = response.json()
        assert "id" in category
        assert category["name"] == category_payload["name"]
        # Use get to avoid assertion error if description is missing in response
        assert category.get("description") == category_payload["description"]
        created_resources["category_id"] = category["id"]

        # 2. Retrieve category - validate
        response = requests.get(f"{BASE_URL}/menu/categories/{category['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200
        fetched_cat = response.json()
        assert fetched_cat["id"] == category["id"]
        assert fetched_cat["name"] == category_payload["name"]
        assert fetched_cat.get("description") == category_payload["description"]

        # 3. Update category
        update_category_payload = {"name": f"Updated Category {uuid.uuid4()}", "description": "Updated description"}
        response = requests.put(
            f"{BASE_URL}/menu/categories/{category['id']}", json=update_category_payload, headers=headers, timeout=TIMEOUT
        )
        assert response.status_code == 200
        updated_category = response.json()
        assert updated_category.get("id") == category["id"]
        assert updated_category["name"] == update_category_payload["name"]
        assert updated_category.get("description") == update_category_payload["description"]

        # 4. Create a menu item assigned to the category
        menu_item_payload = {
            "name": f"Test Pizza {uuid.uuid4()}",
            "description": "Delicious test pizza",
            "category_id": created_resources["category_id"],
            "price": 9.99,
            "available": True
        }
        response = requests.post(f"{BASE_URL}/menu/items", json=menu_item_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201
        menu_item = response.json()
        assert "id" in menu_item
        assert menu_item["name"] == menu_item_payload["name"]
        created_resources["menu_item_id"] = menu_item["id"]

        # 5. Retrieve menu item
        response = requests.get(f"{BASE_URL}/menu/items/{menu_item['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200
        fetched_item = response.json()
        assert fetched_item["id"] == menu_item["id"]
        assert fetched_item["category_id"] == created_resources["category_id"]
        assert fetched_item["available"] is True
        assert abs(fetched_item["price"] - menu_item_payload["price"]) < 0.001

        # 6. Update menu item availability and price
        update_item_payload = {"available": False, "price": 11.99, "description": "Updated test pizza description"}
        response = requests.put(
            f"{BASE_URL}/menu/items/{menu_item['id']}", json=update_item_payload, headers=headers, timeout=TIMEOUT
        )
        assert response.status_code == 200
        updated_item = response.json()
        assert updated_item["available"] is False
        assert abs(updated_item["price"] - 11.99) < 0.001
        assert updated_item["description"] == update_item_payload["description"]

        # 7. Create a product option for the menu item
        product_option_payload = {
            "menu_item_id": menu_item["id"],
            "name": f"Extra Cheese {uuid.uuid4()}",
            "price": 1.50,
            "available": True
        }
        response = requests.post(f"{BASE_URL}/menu/product-options", json=product_option_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201
        product_option = response.json()
        assert product_option["name"] == product_option_payload["name"]
        created_resources["product_option_id"] = product_option["id"]

        # 8. Retrieve product option
        response = requests.get(f"{BASE_URL}/menu/product-options/{product_option['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200
        fetched_option = response.json()
        assert fetched_option["id"] == product_option["id"]
        assert fetched_option["menu_item_id"] == menu_item["id"]
        assert abs(fetched_option["price"] - product_option_payload["price"]) < 0.001

        # 9. Update product option availability and price
        update_option_payload = {"available": False, "price": 2.00, "name": "Updated Extra Cheese"}
        response = requests.put(
            f"{BASE_URL}/menu/product-options/{product_option['id']}", json=update_option_payload, headers=headers, timeout=TIMEOUT
        )
        assert response.status_code == 200
        updated_option = response.json()
        assert updated_option["available"] is False
        assert abs(updated_option["price"] - 2.00) < 0.001
        assert updated_option["name"] == update_option_payload["name"]

        # 10. Delete product option
        response = requests.delete(f"{BASE_URL}/menu/product-options/{product_option['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 204
        created_resources["product_option_id"] = None

        # 11. Delete menu item
        response = requests.delete(f"{BASE_URL}/menu/items/{menu_item['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 204
        created_resources["menu_item_id"] = None

        # 12. Delete category
        response = requests.delete(f"{BASE_URL}/menu/categories/{category['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 204
        created_resources["category_id"] = None

        # 13. Verify deletions: category
        response = requests.get(f"{BASE_URL}/menu/categories/{category['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 404
        # 14. Verify deletions: menu item
        response = requests.get(f"{BASE_URL}/menu/items/{menu_item['id']}", headers=headers, timeout=TIMEOUT)
        assert response.status_code == 404
        # 15. Verify deletions: product option (already deleted)
        # No need to verify again

    finally:
        cleanup()

menu_management_api_crud_operations()
