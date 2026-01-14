# Market Intelligence MCP Server

This is a Model Context Protocol (MCP) server that bridges Large Language Models with real-time financial data using the CoinGecko API.

## Features

- **Tools**:
  - `get_crypto_price(asset_id, vs_currencies)`: Fetch live crypto prices.
  - `analyze_spread(bid_price, ask_price)`: Calculate spread and liquidity metrics.
- **Resources**:
  - `market://status`: Check connectivity and API status.

## Prerequisites

- Python 3.10+
- A CoinGecko API Key (Demo keys work).

## Setup

1. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Ensure your `.env` file contains your CoinGecko API key:
   ```env
   CRYPTO_API_KEY=your_api_key_here
   ```

## Configuration for Claude Desktop

To use this server with the Claude Desktop App, add the following configuration to your Claude config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the `market-intelligence` server entry:

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "python",
      "args": ["S:\\Market-MCP\\Market-MCP-Test\\market_server.py"],
      "env": {
        "CRYPTO_API_KEY": "CG-NoxBkyQrpsssKisLFbi9fb3U"
      }
    }
  }
}
```

*Note: You may need to use the absolute path to your Python executable if the global python version doesn't have the dependencies installed. For example:*
`"command": "S:\\Market-MCP\\.venv\\Scripts\\python.exe"`

## Running Manually

You can test the server runs by executing:
```bash
python market_server.py
```
It uses stdio transport, so it will wait for input.
