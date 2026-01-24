"""
Exchange Connectivity Tools

MCP tools for fetching real-time market data from crypto exchanges via CCXT.
Provides live order book and ticker data for HFT analytics.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import ccxt.async_support as ccxt
from mcp.server.fastmcp import FastMCP

# Supported exchanges options for the user
SUPPORTED_EXCHANGES = ["binance", "kraken", "coinbase", "kucoin", "bybit", "okx"]

async def _get_exchange(exchange_id: str):
    """
    Factory to get an exchange instance with proper configuration.
    """
    import sys
    exchange_id = exchange_id.lower()
    if exchange_id not in ccxt.exchanges:
        raise ValueError(f"Exchange '{exchange_id}' not found in CCXT.")
    
    # Instantiate the exchange class dynamically with config
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'enableRateLimit': True,  # Respect rate limits
        'timeout': 30000,  # 30 second timeout (default is 10000)
        'options': {
            'defaultType': 'spot',  # Use spot market by default
        },
        # CRITICAL: Skip automatic market loading to avoid firewall issues
        # This prevents CCXT from calling /exchangeInfo during init
        'fetchMarkets': False,
    })
    
    print(f"[DEBUG] Created {exchange_id} instance (skip metadata load)", file=sys.stderr)
    return exchange

# --- Shared Tools (Accessible by Dashboard & MCP) ---

async def fetch_orderbook(
    symbol: str,
    exchange: str = "binance",
    limit: int = 20
) -> str:
    """
    Fetch real-time Level 2 order book data for a trading pair.
    
    This data is the raw fuel for 'analyze_orderbook' and 'detect_anomalies'.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT', 'ETH/USD').
        exchange: Exchange name (default: 'binance').
        limit: Depth of the order book (default: 20).
        
    Returns:
        JSON string with 'bids', 'asks', 'symbol', and 'timestamp'.
    """
    exchange_instance = None
    try:
        import sys
        print(f"[DEBUG] Attempting to fetch orderbook for {symbol} from {exchange}", file=sys.stderr)
        
        exchange_instance = await _get_exchange(exchange)
        print(f"[DEBUG] Exchange instance created: {exchange}", file=sys.stderr)
        
        # CCXT expects unified symbols. Upper case usually works best.
        formatted_symbol = symbol.upper()
        
        # Fetch order book with timeout handling
        print(f"[DEBUG] Fetching orderbook for {formatted_symbol}...", file=sys.stderr)
        orderbook = await exchange_instance.fetch_order_book(formatted_symbol, limit)
        print(f"[DEBUG] Orderbook fetched successfully!", file=sys.stderr)
        
        result = {
            "symbol": formatted_symbol,
            "exchange": exchange,
            "bids": orderbook["bids"],
            "asks": orderbook["asks"],
            "nonce": orderbook.get("nonce"),
            "timestamp": datetime.now().isoformat(),
            "fetched_at": orderbook.get("datetime")
        }
        
        return json.dumps(result)
        
    except ImportError as e:
        import sys
        print(f"[ERROR] Import error: {e}", file=sys.stderr)
        return json.dumps({
            "error": "CCXT library not installed",
            "message": "Please install ccxt: pip install ccxt"
        })
    except Exception as e:
        import sys
        print(f"[ERROR] Exception in fetch_orderbook: {type(e).__name__}: {e}", file=sys.stderr)
        return json.dumps({
            "error": f"Failed to fetch order book from {exchange}",
            "details": str(e),
            "error_type": type(e).__name__,
            "hint": f"Check symbol format (e.g., BTC/USDT) and exchange support ({exchange})"
        })
    finally:
        if exchange_instance:
            try:
                await exchange_instance.close()
            except Exception as e:
                import sys
                print(f"[WARN] Error closing exchange: {e}", file=sys.stderr)

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
