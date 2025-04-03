# MCP Odoo Integration

This project integrates an MCP client with an MCP server to retrieve available products from the Odoo eCommerce API.

## Project Structure

```
mcp-odoo-integration
├── client
│   ├── src
│   │   ├── gemini_client.py
│   │   ├── config.py
│   │   └── utils.py
│   ├── .env
│   ├── requirements.txt
│   └── README.md
├── server
│   ├── src
│   │   ├── odoo_server.py
│   │   ├── odoo_api.py
│   │   └── config.py
│   ├── .env 
│   ├── requirements.txt
│   └── README.md
├── .gitignore
└── README.md
```

## Client Setup

1. Navigate to the `client` directory.
2. Create a `.env` file with your Odoo API credentials.
3. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```

## Server Setup

1. Navigate to the `server` directory.
2. Create a `.env` file with your Odoo API credentials.
3. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install all dependencies:
```bash
pip install -r requirements.txt
```

3. Install development dependencies (optional):
```bash
pip install -r requirements.txt[dev]
```

## Usage

- Start the server by running `odoo_server.py`.
- Use the client to connect to the MCP server and retrieve available products from the Odoo API.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.