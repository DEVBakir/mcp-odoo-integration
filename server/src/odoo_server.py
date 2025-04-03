from mcp.server.fastmcp import FastMCP
from odoo_api import fetch_available_products

# Initialize the FastMCP server
mcp = FastMCP("odoo")

@mcp.tool()
async def get_products() -> str:
    """Retrieve available products from the Odoo eCommerce API."""
    products = await fetch_available_products()
    if not products:
        return "No products found."
    return products

if __name__ == "__main__":
    mcp.run(transport='stdio')