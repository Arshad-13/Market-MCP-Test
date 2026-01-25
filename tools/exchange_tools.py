"""
Exchange Connectivity Tools

MCP tools for fetching real-time market data from crypto exchanges.
**UPDATED:** Uses direct HTTP API calls instead of CCXT to bypass initialization issues.

FEATURES (v1.26.2):
- Direct HTTP API calls (no CCXT market loading)
- Multi-exchange fallback (Binance → Kraken → Coinbase)
- Works everywhere (no subprocess restrictions)
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from mcp.server.fastmcp import FastMCP

# Exchange API endpoints
EXCHANGE_APIS = {
    "binance": {
        "orderbook": "https://api.binance.com/api/v3/depth",
        "ticker": "https://api.binance.com/api/v3/ticker/24hr"
    },
    "kraken": {
        "orderbook": "https://api.kraken.com/0/public/Depth",
        "ticker": "https://api.kraken.com/0/public/Ticker"
    },
    "coinbase": {
        "orderbook": "https://api.exchange.coinbase.com/products/{symbol}/book",
        "ticker": "https://api.exchange.coinbase.com/products/{symbol}/ticker"
    }
}

# Exchange fallback priority order
EXCHANGE_FALLBACK_ORDER = ["binance", "kraken", "coinbase"]

# Supported exchanges
SUPPORTED_EXCHANGES = list(EXCHANGE_APIS.keys())


def _convert_symbol(symbol: str, exchange: str) -> str:
    """Convert unified symbol format to exchange-specific format"""
    # BTC/USDT → exchange-specific
    if exchange == "binance":
        return symbol.replace("/", "").upper()  # BTCUSDT
    elif exchange == "kraken":
        # Kraken uses XXBTZUSD format, but also accepts XBTUSD
        base, quote = symbol.split("/")
        if base == "BTC":
            base = "XBT"
        return base.upper() + quote.upper()
    elif exchange == "coinbase":
        return symbol  # BTC-USDT format
    return symbol


async def _fetch_binance_orderbook(symbol: str, limit: int) -> Dict[str, Any]:
    """Fetch orderbook from Binance using direct API"""
    import sys
    
    symbol_formatted = _convert_symbol(symbol, "binance")
    url = EXCHANGE_APIS["binance"]["orderbook"]
    params = {"symbol": symbol_formatted, "limit": limit}
    
    print(f"[DEBUG] Binance API: GET {url}?symbol={symbol_formatted}&limit={limit}", file=sys.stderr)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "bids": [[float(p), float(q)] for p, q in data.get("bids", [])],
            "asks": [[float(p), float(q)] for p, q in data.get("asks", [])],
            "timestamp": data.get("lastUpdateId")
        }


async def _fetch_kraken_orderbook(symbol: str, limit: int) -> Dict[str, Any]:
    """Fetch orderbook from Kraken using direct API"""
    import sys
    
    symbol_formatted = _convert_symbol(symbol, "kraken")
    url = EXCHANGE_APIS["kraken"]["orderbook"]
    params = {"pair": symbol_formatted, "count": limit}
    
    print(f"[DEBUG] Kraken API: GET {url}?pair={symbol_formatted}&count={limit}", file=sys.stderr)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            raise Exception(f"Kraken API error: {data['error']}")
        
        # Kraken returns data with pair as key
        result_key = list(data["result"].keys())[0]
        orderbook = data["result"][result_key]
        
        return {
            "bids": [[float(p), float(q)] for p, q, _ in orderbook.get("bids", [])],
            "asks": [[float(p), float(q)] for p, q, _ in orderbook.get("asks", [])],
            "timestamp": None
        }


async def _fetch_coinbase_orderbook(symbol: str, limit: int) -> Dict[str, Any]:
    """Fetch orderbook from Coinbase using direct API"""
    import sys
    
    symbol_formatted = symbol.replace("/", "-")  # BTC/USDT → BTC-USDT
    url = EXCHANGE_APIS["coinbase"]["orderbook"].format(symbol=symbol_formatted)
    params = {"level": 2}  # Level 2 = top 50 bids/asks
    
    print(f"[DEBUG] Coinbase API: GET {url}", file=sys.stderr)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "bids": [[float(p), float(q)] for p, q, _ in data.get("bids", [])[:limit]],
            "asks": [[float(p), float(q)] for p, q, _ in data.get("asks", [])[:limit]],
            "timestamp": data.get("sequence")
        }


# --- Shared Tools (Accessible by Dashboard & MCP) ---

async def fetch_orderbook(
    symbol: str,
    exchange: str = "binance",
    limit: int = 20,
    fallback: bool = True
) -> str:
    """
    Fetch real-time Level 2 order book data with multi-exchange fallback.
    
    **NEW:** Uses direct HTTP API calls (no CCXT dependency issues!)
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT', 'ETH/USD').
        exchange: Exchange name (default: 'binance').
        limit: Depth of the order book (default: 20).
        fallback: Enable multi-exchange fallback (default: True).
        
    Returns:
        JSON string with 'bids', 'asks', 'symbol', and 'timestamp'.
    """
    # If fallback is enabled, try multiple exchanges
    exchanges_to_try = [exchange]
    if fallback:
        # Add fallback exchanges
        exchanges_to_try = [exchange] + [
            ex for ex in EXCHANGE_FALLBACK_ORDER if ex != exchange
        ]
    
    last_error = None
    
    for attempt_exchange in exchanges_to_try:
        try:
            import sys
            print(f"[INFO] Fetching orderbook for {symbol} from {attempt_exchange}", file=sys.stderr)
            
            # Call exchange-specific function
            if attempt_exchange == "binance":
                orderbook = await _fetch_binance_orderbook(symbol, limit)
            elif attempt_exchange == "kraken":
                orderbook = await _fetch_kraken_orderbook(symbol, limit)
            elif attempt_exchange == "coinbase":
                orderbook = await _fetch_coinbase_orderbook(symbol, limit)
            else:
                raise ValueError(f"Exchange {attempt_exchange} not supported yet")
            
            print(f"[SUCCESS] Got {len(orderbook['bids'])} bids, {len(orderbook['asks'])} asks", file=sys.stderr)
            
            result = {
                "symbol": symbol.upper(),
                "exchange": attempt_exchange,
                "requested_exchange": exchange,
                "bids": orderbook["bids"],
                "asks": orderbook["asks"],
                "timestamp": datetime.now().isoformat(),
                "fallback_used": attempt_exchange != exchange
            }
            
            return json.dumps(result)
            
        except Exception as e:
            import sys
            last_error = e
            print(f"[ERROR] {attempt_exchange} failed: {type(e).__name__}: {e}", file=sys.stderr)
            
            # If there are more exchanges to try, continue
            if attempt_exchange != exchanges_to_try[-1]:
                print(f"[INFO] Trying next exchange...", file=sys.stderr)
                continue
    
    # All exchanges failed
    import sys
    print(f"[ERROR] All exchanges failed. Last error: {last_error}", file=sys.stderr)
    return json.dumps({
        "error": "Failed to fetch order book from all exchanges",
        "requested_exchange": exchange,
        "attempted_exchanges": exchanges_to_try,
        "last_error": str(last_error),
        "error_type": type(last_error).__name__
    })


async def fetch_ticker(symbol: str, exchange: str = "binance") -> str:
    """
    Fetch the current ticker (price, volume, high/low) for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT').
        exchange: Exchange name (default: 'binance').
        
    Returns:
        JSON string with ticker data.
    """
    exchange_instance = None
    try:
        import sys
        print(f"[DEBUG] Fetching ticker for {symbol} from {exchange}", file=sys.stderr)
        
        exchange_instance = await _get_exchange(exchange)
        formatted_symbol = symbol.upper()
        
        ticker = await exchange_instance.fetch_ticker(formatted_symbol)
        print(f"[DEBUG] Ticker fetched successfully for {formatted_symbol}", file=sys.stderr)
        
        result = {
            "symbol": formatted_symbol,
            "exchange": exchange,
            "last_price": ticker.get("last"),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "high": ticker.get("high"),
            "low": ticker.get("low"),
            "volume": ticker.get("baseVolume"),
            "percentage_change": ticker.get("percentage"),
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result)
        
    except Exception as e:
        import sys
        print(f"[ERROR] Exception in fetch_ticker: {type(e).__name__}: {e}", file=sys.stderr)
        return json.dumps({
            "error": f"Failed to fetch ticker from {exchange}",
            "details": str(e),
            "error_type": type(e).__name__
        })
    finally:
        if exchange_instance:
            try:
                await exchange_instance.close()
            except Exception as e:
                import sys
                print(f"[WARN] Error closing exchange in fetch_ticker: {e}", file=sys.stderr)

def list_supported_exchanges() -> str:
    """
    List recommended exchanges supported by this server.
    
    Returns:
        JSON string with a list of exchange IDs.
    """
    return json.dumps({
        "recommended": SUPPORTED_EXCHANGES,
        "note": "Most CCXT-supported exchanges work, but these are verified."
    })

def register_exchange_tools(mcp: FastMCP) -> None:
    """
    Register exchange connectivity MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(fetch_orderbook)
    mcp.tool()(fetch_ticker)
    mcp.tool()(list_supported_exchanges)
