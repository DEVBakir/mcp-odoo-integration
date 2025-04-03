# MCP Odoo Integration

This project integrates an MCP client with an MCP server to retrieve available products from the Odoo eCommerce API.

## Project Structure

```
mcp-odoo-integration
├── client
│   ├── src
│   │   ├── gemini_client.py
│   │   └── utils.py
├── server
│   ├── src
│   │   ├── odoo_server.py
│   │   ├── odoo_api.py
├── .gitignore
├── requirements.txt
└── README.md
```


## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install all dependencies:
```bash
pip install -r requirements.txt
```



## Usage


## Client Start

1. Navigate to the `client` directory.
2. python3 gemini_client.py

## Server Start

1. Navigate to the `server` directory.
2. python3 odoo_server.py- Use the client to connect to the MCP server and retrieve available products from the Odoo API.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
