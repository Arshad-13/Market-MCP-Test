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
    Factory to get an exchange instance.
    """
    exchange_id = exchange_id.lower()
    if exchange_id not in ccxt.exchanges:
        raise ValueError(f"Exchange '{exchange_id}' not found in CCXT.")
    
    # Instantiate the exchange class dynamically
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
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
        exchange_instance = await _get_exchange(exchange)
        
        # CCXT expects unified symbols. Upper case usually works best.
        formatted_symbol = symbol.upper()
        
        # Fetch order book
        orderbook = await exchange_instance.fetch_order_book(formatted_symbol, limit)
        
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
        
    except ImportError:
        return json.dumps({
            "error": "CCXT library not installed",
            "message": "Please install ccxt: pip install ccxt"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch order book from {exchange}",
            "details": str(e),
            "hint": f"Check symbol format (e.g., BTC/USDT) and exchange support ({exchange})"
        })
    finally:
        if exchange_instance:
            await exchange_instance.close()

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
        exchange_instance = await _get_exchange(exchange)
        formatted_symbol = symbol.upper()
        
        ticker = await exchange_instance.fetch_ticker(formatted_symbol)
        
        result = {
            "symbol": formatted_symbol,
            "exchange": exchange,
            "last_price": ticker.get("last"),
            "high": ticker.get("high"),
            "low": ticker.get("low"),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "volume": ticker.get("baseVolume"),
            "quote_volume": ticker.get("quoteVolume"),
            "percentage_change": ticker.get("percentage"),
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch ticker from {exchange}",
            "details": str(e)
        })
    finally:
        if exchange_instance:
            await exchange_instance.close()

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
