import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("CRYPTO_API_KEY")

# Initialize the MCP Server
mcp = FastMCP("Market Intelligence")

# Constants
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

def get_headers():
    headers = {"accept": "application/json"}
    if API_KEY:
        headers["x-cg-demo-api-key"] = API_KEY
    return headers

@mcp.tool()
async def get_crypto_price(asset_id: str, vs_currencies: str = "usd") -> str:
    """
    Fetch live cryptocurrency prices from CoinGecko.
    
    Args:
        asset_id: The ID of the crypto asset (e.g., 'bitcoin', 'ethereum').
        vs_currencies: Comma-separated target currencies (default: 'usd').
    """
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": asset_id,
        "vs_currencies": vs_currencies,
        "include_24hr_change": "true"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=get_headers())
            response.raise_for_status()
            data = response.json()
            return str(data)
        except httpx.HTTPError as e:
            return f"Error fetching price: {str(e)}"

@mcp.tool()
def analyze_spread(bid_price: float, ask_price: float) -> str:
    """
    Compute market microstructure metrics based on bid and ask prices.
    
    Args:
        bid_price: The highest price a buyer is willing to pay.
        ask_price: The lowest price a seller is willing to accept.
    """
    if bid_price >= ask_price:
        return "Error: Bid price must be lower than ask price for a valid spread analysis."
        
    spread = ask_price - bid_price
    mid_price = (ask_price + bid_price) / 2
    spread_bps = (spread / mid_price) * 10000
    
    analysis = {
        "spread_absolute": round(spread, 6),
        "mid_price": round(mid_price, 6),
        "spread_basis_points": round(spread_bps, 2),
        "liquidity_classification": "High" if spread_bps < 5 else "Medium" if spread_bps < 20 else "Low"
    }
    
    return str(analysis)

@mcp.resource("market://status")
async def get_connectivity_status() -> str:
    """
    Check the connectivity status of the Market Intelligence Server and CoinGecko API.
    """
    status = {
        "server_status": "online",
        "api_key_configured": bool(API_KEY),
        "coingecko_api_reachable": "unknown"
    }
    
    # Simple ping to CoinGecko
    url = f"{COINGECKO_BASE_URL}/ping"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=get_headers(), timeout=5.0)
            if response.status_code == 200:
                status["coingecko_api_reachable"] = True
            else:
                status["coingecko_api_reachable"] = False
        except:
            status["coingecko_api_reachable"] = False
            
    return str(status)

if __name__ == "__main__":
    mcp.run()
