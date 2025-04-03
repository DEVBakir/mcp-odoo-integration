import os
import logging
import xmlrpc.client
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Odoo connection settings loaded from environment variables
ODOO_URL = os.getenv("ODOO_URL")  # Default to localhost if not set
ODOO_DB = os.getenv("ODOO_DB")  # Default database name
API_KEY = os.getenv("API_KEY")  # API key must be set in the environment
ODOO_USERNAME = os.getenv("ODOO_USERNAME")  # Default username

# Log successful configuration
logger.info(f"Successfully loaded configuration for database: {ODOO_DB}")

def get_odoo_connection() -> tuple[xmlrpc.client.ServerProxy, int]:
    """Create and return Odoo XML-RPC connection using API key."""
    try:
        common_endpoint = f'{ODOO_URL}/xmlrpc/2/common'
        logger.info(f"Connecting to Odoo at: {common_endpoint}")
        
        common = xmlrpc.client.ServerProxy(
            common_endpoint,
            allow_none=True,
            use_datetime=True
        )
        
        # Authenticate with username and API key
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, API_KEY, {})
        if not uid:
            raise ConnectionError("Authentication failed")
            
        logger.info(f"Successfully authenticated with UID: {uid}")
        
        models = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/object',
            allow_none=True,
            use_datetime=True
        )
        
        return models, uid
    except Exception as e:
        logger.error(f"Failed to connect to Odoo: {str(e)}")
        raise

async def fetch_available_products() -> str:
    """Fetch available products from Odoo eCommerce using XML-RPC."""
    try:
        # Establish connection to Odoo
        models, uid = get_odoo_connection()

        # Search for published products
        product_ids = models.execute_kw(
            ODOO_DB, uid, API_KEY,  # Use API key instead of password
            'product.template',  # Model name
            'search',  # Method name
            [[['website_published', '=', True]]]  # Domain filter
        )

        if not product_ids:
            return "No published products found."

        # Read product details
        products = models.execute_kw(
            ODOO_DB, uid, API_KEY,  # Use API key instead of password
            'product.template',  # Model name
            'read',  # Method name
            [product_ids],  # List of product IDs
            {'fields': ['name', 'list_price', 'description_sale', 'default_code']}  # Fields to fetch
        )

        # Format product information
        formatted_products = []
        for product in products:
            product_info = (
                f"Product: {product.get('name', 'N/A')}\n"
                f"SKU: {product.get('default_code', 'N/A')}\n"
                f"Price: ${product.get('list_price', 0.0):.2f}\n"
                f"Description: {product.get('description_sale', 'No description available')}\n"
            )
            formatted_products.append(product_info)

        return "\n---\n".join(formatted_products) if formatted_products else "No product details available."

    except Exception as e:
        logger.error(f"Error in fetch_available_products: {str(e)}")
        return f"Error fetching products: {str(e)}"