def format_product_data(product):
    """Format product data for display."""
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "price": product.get("list_price"),
        "currency": product.get("currency_id", {}).get("name", "USD"),
    }

def handle_api_error(response):
    """Handle errors from API responses."""
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def parse_response_data(response_data):
    """Parse and return the relevant data from the API response."""
    return [format_product_data(product) for product in response_data.get("products", [])]