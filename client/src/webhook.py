import asyncio
import os
import logging
import httpx
import redis
from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from gemini_client import GeminiClient  # Import your class

logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Load config
config = {
    'VERIFY_TOKEN': '12345678',  # WhatsApp Webhook Token
    'WHATSAPP_API_TOKEN': os.getenv('WHATSAPP_API_TOKEN')  # WhatsApp API Token
}

# Initialize FastAPI
app = FastAPI()
current_dir = os.path.dirname(os.path.abspath(__file__))
server_path = os.path.abspath(os.path.join(current_dir, "../../server/src/odoo_server.py"))
client = None  # Initialize later

# Initialize Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


class QueryRequest(BaseModel):
    query: str
    user_id: str  # Required to track conversation per user


@app.on_event("startup")
async def startup_event():
    """Automatically connect to the MCP server on startup."""
    global client
    client = GeminiClient()
    try:
        logging.info("Connecting to MCP server...")
        await client.connect_to_server(server_path)
        logging.info("Connected to MCP server.")
    except Exception as e:
        logging.error(f"Failed to connect to MCP server: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully close the connection to MCP server when API stops."""
    global client
    if client:
        logging.info("Disconnecting from MCP server...")
        await client.close()
        logging.info("MCP server disconnected.")


async def process_user_query(user_id: str, query: str):
    """Retrieve past messages from Redis and build conversation context."""
    past_messages = redis_client.lrange(f"chat_history:{user_id}", 0, -1)
    print(past_messages)
    # Build conversation context
    system_instruction = "You are an AI assistant having a continuous conversation with the user. Remember past context and provide helpful responses."
    context = system_instruction +"\n".join(past_messages) + f"\nUser: {query}"

    # Get AI response
    response = await client.process_query(context)

    # Store new messages in Redis
    redis_client.rpush(f"chat_history:{user_id}", f"User: {query}")
    redis_client.rpush(f"chat_history:{user_id}", f"AI: {response}")

    return response


@app.post("/query")
async def process_query(request: QueryRequest):
    """Process a query and return AI response with conversation history."""
    try:
        response = await process_user_query(request.user_id, request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
async def get_products():
    """Retrieve available products."""
    try:
        products = await client.get_available_products()
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    try:
        data = await request.json()
        logging.debug(f"Received Webhook Event: {data}")

        # Extract the message body and sender's phone number
        message_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        sender_id = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

        logging.debug(f"Message: {message_body}, Sender: {sender_id}")

        # Get AI-generated response with context
        reply_message = await process_user_query(sender_id, message_body)

        # Send WhatsApp message
        await send_whatsapp_message(sender_id, reply_message)

        return {"status": "Message processed"}

    except KeyError as e:
        logging.error(f"KeyError: {e} - Missing key in the webhook payload")
        return {"status": "Error", "detail": str(e)}


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """Verify webhook for WhatsApp"""
    if hub_mode == "subscribe" and hub_verify_token == config["VERIFY_TOKEN"]:
        return int(hub_challenge)  # WhatsApp expects this as a number
    return {"error": "Forbidden"}, 403


async def send_whatsapp_message(recipient_id: str, message: str):
    """Send a WhatsApp message using the WhatsApp Business API."""
    url = "https://graph.facebook.com/v15.0/592460250612769/messages"  # Replace with your phone number ID
    headers = {
        "Authorization": f"Bearer {os.getenv("WHATSAPP_API_TOKEN")}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info(f"Message sent successfully: {response.json()}")
        else:
            logging.error(f"Failed to send message: {response.status_code}, {response.text}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
