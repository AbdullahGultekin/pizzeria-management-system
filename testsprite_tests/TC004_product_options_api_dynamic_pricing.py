import requests
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_product_options_api_dynamic_pricing():
    headers = {
        "Content-Type": "application/json",
    }

    # Step 1: Create product options for each category: vlees, bijgerecht, sauzen, garnering
    product_option_categories = ["vlees", "bijgerecht", "sauzen", "garnering"]
    created_options = []

    try:
        for category in product_option_categories:
            option_data = {
                "name": f"Test {category} option",
                "category": category,
                "price": 1.50  # example dynamic price for testing
            }
            resp = requests.post(
                f"{BASE_URL}/api/extras",
                headers=headers,
                timeout=TIMEOUT,
                data=json.dumps(option_data)
            )
            assert resp.status_code == 201, f"Failed to create {category} option: {resp.text}"
            created_option = resp.json()
            assert created_option.get("id") is not None, "Created option missing 'id'"
            assert created_option.get("price") == 1.50, "Option price mismatch"
            assert created_option.get("category") == category, "Option category mismatch"
            created_options.append(created_option)

        # Step 2: Retrieve the list of all product options and confirm our created options exist with correct prices and categories
        resp = requests.get(
            f"{BASE_URL}/api/extras",
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Failed to get product options: {resp.text}"
        all_options = resp.json()
        option_ids = [o["id"] for o in all_options]
        for created_option in created_options:
            assert created_option["id"] in option_ids, f"Option {created_option['id']} not found in list"
            # Verify correct association and price in detail
            matching = next((o for o in all_options if o["id"] == created_option["id"]), None)
            assert matching is not None, "Option should be present"
            assert matching["category"] == created_option["category"], "Category mismatch in list"
            assert matching["price"] == created_option["price"], "Price mismatch in list"

        # Step 3: Test dynamic price update (simulate price change) for one option
        update_data = {
            "price": 2.25
        }
        option_to_update = created_options[0]
        resp = requests.put(
            f"{BASE_URL}/api/extras/{option_to_update['id']}",
            headers=headers,
            timeout=TIMEOUT,
            data=json.dumps(update_data)
        )
        assert resp.status_code == 200, f"Failed to update option price: {resp.text}"
        updated_option = resp.json()
        assert updated_option["price"] == 2.25, "Price update did not apply"

        # Step 4: Verify dynamic pricing is reflected when retrieving this single option
        resp = requests.get(
            f"{BASE_URL}/api/extras/{option_to_update['id']}",
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Failed to get updated option: {resp.text}"
        fetched_option = resp.json()
        assert fetched_option["price"] == 2.25, "Fetched option price mismatch after update"
        assert fetched_option["category"] == option_to_update["category"], "Fetched category mismatch"

    finally:
        # Cleanup: Delete all created options to maintain test isolation
        for option in created_options:
            try:
                resp_del = requests.delete(
                    f"{BASE_URL}/api/extras/{option['id']}",
                    headers=headers,
                    timeout=TIMEOUT
                )
                # Accept 200 or 204 as success for deletion
                assert resp_del.status_code in (200, 204), f"Failed to delete option {option['id']}: {resp_del.text}"
            except Exception:
                pass  # ignore errors during cleanup to avoid masking test failures

test_product_options_api_dynamic_pricing()
