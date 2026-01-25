"""
Market Intelligence MCP Server

A comprehensive market analysis server merging Genesis2025 HFT analytics
with broad market intelligence tools.
"""

import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Import tool registration functions
from tools import (
    register_price_tools,
    register_microstructure_tools,
    register_anomaly_tools,
    register_sentiment_tools,
    register_defi_tools,
    register_exchange_tools,
    register_ml_tools,
    register_portfolio_tools,
    register_alert_tools,
    register_trading_tools,
    register_strategy_tools,
    register_agent_tools,
    register_streaming_tools,
)
from prompts import register_prompts
from core.background_service import monitor
from core.database import db

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the MCP Server
mcp = FastMCP("Market Intelligence")

# Register all tools
register_price_tools(mcp)
register_microstructure_tools(mcp)
register_anomaly_tools(mcp)
register_sentiment_tools(mcp)
register_defi_tools(mcp)
register_exchange_tools(mcp)
register_ml_tools(mcp)
register_portfolio_tools(mcp)
register_alert_tools(mcp)
register_trading_tools(mcp)
register_strategy_tools(mcp)
register_agent_tools(mcp)
register_streaming_tools(mcp)

# Register prompts
register_prompts(mcp)

# Attempt to start background monitor on startup (if supported)
# or just start it now (if we are in an async loop, which we aren't yet at module level)
# We'll use a resource that triggers it, or relies on lazy start.
# For now, let's expose a tool to ensure it's started if needed, 
# but actually FastMCP might support a customized run. 
# We'll add a simple startup log.
print("Market Intelligence Server Initialized.")

# System Resources
@mcp.resource("market://status")
async def get_connectivity_status() -> str:
    """
    Check the connectivity status of the Market Intelligence Server and external APIs.
    """
    api_key_configured = bool(os.getenv("CRYPTO_API_KEY"))
    status = {
        "server_status": "online",
        "api_key_configured": api_key_configured,
        "coingecko_status": "unknown"
    }
    
    # Simple ping to CoinGecko
    url = "https://api.coingecko.com/api/v3/ping"
    headers = {"accept": "application/json"}
    if api_key_configured:
        headers["x-cg-demo-api-key"] = os.getenv("CRYPTO_API_KEY")
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=5.0)
            status["coingecko_status"] = "reachable" if response.status_code == 200 else f"error_{response.status_code}"
        except Exception as e:
            status["coingecko_status"] = f"unreachable_{str(e)}"
            
    return str(status)

def main():
    """Main entry point - currently supports stdio mode only"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Intelligence MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio"],
        default="stdio",
        help="Server mode: stdio (for Claude Desktop subprocess)"
    )
    
    args = parser.parse_args()
    
    # Run in STDIO mode (JSON-RPC communication)
    mcp.run()

if __name__ == "__main__":
    main()
