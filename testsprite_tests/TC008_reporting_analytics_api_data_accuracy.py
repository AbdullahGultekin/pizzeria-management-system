import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Assuming JWT authentication token needed; set your token here if applicable
TOKEN = None  # e.g. "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
HEADERS = {
    "Content-Type": "application/json",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def test_reporting_analytics_api_data_accuracy():
    try:
        # Test generation of Daily Report with accurate product statistics, hourly breakdowns, and revenue tracking
        daily_report_resp = requests.get(
            f"{BASE_URL}/api/reports/daily",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        assert daily_report_resp.status_code == 200, f"Daily report failed: {daily_report_resp.text}"
        daily_data = daily_report_resp.json()

        # Basic sanity checks on daily report content structure
        assert "date" in daily_data, "Daily report missing 'date' field"
        assert "product_statistics" in daily_data, "Daily report missing 'product_statistics'"
        assert "hourly_breakdown" in daily_data, "Daily report missing 'hourly_breakdown'"
        assert "revenue" in daily_data, "Daily report missing 'revenue'"

        # Validate date is today or yesterday depending on implementation
        daily_report_date = datetime.strptime(daily_data["date"], "%Y-%m-%d")
        assert daily_report_date.date() in {datetime.utcnow().date(), (datetime.utcnow() - timedelta(days=1)).date()}, \
            "Daily report has unexpected date"

        # Validate product_statistics is a list and each element has expected keys
        assert isinstance(daily_data["product_statistics"], list), "product_statistics should be a list"
        for product_stat in daily_data["product_statistics"]:
            assert "product_id" in product_stat, "product_statistics item missing 'product_id'"
            assert "quantity_sold" in product_stat, "product_statistics item missing 'quantity_sold'"
            assert isinstance(product_stat["quantity_sold"], int), "'quantity_sold' should be int"
            assert "revenue" in product_stat, "product_statistics item missing 'revenue'"
            assert isinstance(product_stat["revenue"], (int, float)), "'revenue' should be a number"

        # Validate hourly_breakdown covers 24 hours and has expected keys
        assert isinstance(daily_data["hourly_breakdown"], list), "hourly_breakdown should be a list"
        assert len(daily_data["hourly_breakdown"]) == 24, "hourly_breakdown should have 24 entries"
        for hour_data in daily_data["hourly_breakdown"]:
            assert "hour" in hour_data, "hourly_breakdown entry missing 'hour'"
            assert 0 <= hour_data["hour"] <= 23, "'hour' should be between 0 and 23"
            assert "orders_count" in hour_data, "hourly_breakdown entry missing 'orders_count'"
            assert isinstance(hour_data["orders_count"], int), "'orders_count' should be int"
            assert "revenue" in hour_data, "hourly_breakdown entry missing 'revenue'"
            assert isinstance(hour_data["revenue"], (int, float)), "'revenue' should be a number"

        assert isinstance(daily_data["revenue"], (int, float)), "daily revenue should be a number"
        assert daily_data["revenue"] >= 0, "daily revenue should be non-negative"

        # Test generation of Monthly Report
        monthly_report_resp = requests.get(
            f"{BASE_URL}/api/reports/monthly",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        assert monthly_report_resp.status_code == 200, f"Monthly report failed: {monthly_report_resp.text}"
        monthly_data = monthly_report_resp.json()

        assert "month" in monthly_data, "Monthly report missing 'month' field"
        assert "product_statistics" in monthly_data, "Monthly report missing 'product_statistics'"
        assert "revenue" in monthly_data, "Monthly report missing 'revenue'"

        # Validate month format YYYY-MM
        datetime.strptime(monthly_data["month"], "%Y-%m")

        # Validate product statistics structure as daily
        assert isinstance(monthly_data["product_statistics"], list), "monthly product_statistics should be a list"
        for prod_stat in monthly_data["product_statistics"]:
            assert "product_id" in prod_stat
            assert "quantity_sold" in prod_stat and isinstance(prod_stat["quantity_sold"], int)
            assert "revenue" in prod_stat and isinstance(prod_stat["revenue"], (int, float))

        assert isinstance(monthly_data["revenue"], (int, float))
        assert monthly_data["revenue"] >= 0

        # Test generation of Z-Report (end of day financial report)
        z_report_resp = requests.get(
            f"{BASE_URL}/api/reports/z-report",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        assert z_report_resp.status_code == 200, f"Z-report failed: {z_report_resp.text}"
        z_data = z_report_resp.json()

        # Basic structure checks for z-report
        assert "date" in z_data
        assert "total_sales" in z_data
        assert "total_orders" in z_data
        assert "product_stats" in z_data
        assert "revenue_breakdown" in z_data

        # Validate types and values
        z_report_date = datetime.strptime(z_data["date"], "%Y-%m-%d")
        assert z_report_date.date() in {datetime.utcnow().date(), (datetime.utcnow() - timedelta(days=1)).date()}

        assert isinstance(z_data["total_sales"], (int, float)) and z_data["total_sales"] >= 0
        assert isinstance(z_data["total_orders"], int) and z_data["total_orders"] >= 0
        assert isinstance(z_data["product_stats"], list)
        for pstat in z_data["product_stats"]:
            assert "product_id" in pstat
            assert "quantity" in pstat and isinstance(pstat["quantity"], int)
            assert "revenue" in pstat and isinstance(pstat["revenue"], (int, float))

        assert isinstance(z_data["revenue_breakdown"], dict)
        for key in ["cash", "card", "voucher", "other"]:
            if key in z_data["revenue_breakdown"]:
                val = z_data["revenue_breakdown"][key]
                assert isinstance(val, (int, float)) and val >= 0

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    except Exception as ex:
        assert False, f"Assertion or parsing failed: {ex}"


test_reporting_analytics_api_data_accuracy()