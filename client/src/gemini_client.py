import asyncio
import os
import httpx
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # Use a valid model name
        self.model_name = "gemini-2.5-pro-exp-03-25"  # Replace with the correct model name

    async def connect_to_server(self, server_script_path: str):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print("Connected to MCP server successfully!")

    async def get_available_products(self):
        """Retrieve available products from the Odoo eCommerce API."""
        if not self.session:
            raise ConnectionError("Not connected to MCP server")
        
        result = await self.session.call_tool("get_products", {})
        return result.content

    async def process_query(self, query: str):
        """Process a query to retrieve product information."""
        try:
            # Get product information
            products = await self.get_available_products()
            
            # Create prompt for Gemini
            prompt = f"""
            You are a helpful shopping assistant from algeria so you speak arabic algerian dilect. Based on this product catalog:
            {products}
            
            Please answer this customer question: {query}
            Provide specific product details when relevant.
            """
            
            # Make a request to the Gemini API
            headers = {
                "Content-Type": "application/json",
            }
            payload = { "contents": [{"parts": [{"text": prompt}]}] }
            
            async with httpx.AsyncClient(timeout=30.0) as client:  # Set timeout to 30 seconds
                response = await client.post(
                    f"{self.api_url}/models/{self.model_name}:generateContent?key={self.api_key}",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Error processing query: {str(Exception)}"

    async def close(self):
        """Close the connection to the MCP server."""
        await self.exit_stack.aclose()
