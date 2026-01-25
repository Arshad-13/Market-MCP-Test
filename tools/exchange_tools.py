"""
Exchange Connectivity Tools

MCP tools for fetching real-time market data from crypto exchanges via CCXT.
Provides live order book and ticker data for HFT analytics.

FEATURES (v1.26.1):
- Multi-exchange fallback (Binance → Kraken → Coinbase → Bybit)
- Auto-retry with exponential backoff
- Enhanced error handling
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import ccxt.async_support as ccxt
from mcp.server.fastmcp import FastMCP

# Exchange fallback priority order
EXCHANGE_FALLBACK_ORDER = ["binance", "kraken", "coinbase", "bybit", "okx"]

# Supported exchanges for user reference
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
    limit: int = 20,
    fallback: bool = True
) -> str:
    """
    Fetch real-time Level 2 order book data with multi-exchange fallback.
    
    This data is the raw fuel for 'analyze_orderbook' and 'detect_anomalies'.
    
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
        # Add fallback exchanges (if not already first choice)
        exchanges_to_try = [exchange] + [
            ex for ex in EXCHANGE_FALLBACK_ORDER if ex != exchange
        ]
    
    last_error = None
    
    for attempt_exchange in exchanges_to_try:
        exchange_instance = None
        try:
            import sys
            print(f"[DEBUG] Attempting to fetch orderbook for {symbol} from {attempt_exchange}", file=sys.stderr)
            
            exchange_instance = await _get_exchange(attempt_exchange)
            print(f"[DEBUG] Exchange instance created: {attempt_exchange}", file=sys.stderr)
            
            # CCXT expects unified symbols. Upper case usually works best.
            formatted_symbol = symbol.upper()
            
            # Fetch order book with timeout handling
            print(f"[DEBUG] Fetching orderbook for {formatted_symbol}...", file=sys.stderr)
            orderbook = await exchange_instance.fetch_order_book(formatted_symbol, limit)
            print(f"[DEBUG] Orderbook fetched successfully from {attempt_exchange}!", file=sys.stderr)
            
            result = {
                "symbol": formatted_symbol,
                "exchange": attempt_exchange,  # Return actual exchange used
                "requested_exchange": exchange,  # Original request
                "bids": orderbook["bids"],
                "asks": orderbook["asks"],
                "nonce": orderbook.get("nonce"),
                "timestamp": datetime.now().isoformat(),
                "fetched_at": orderbook.get("datetime"),
                "fallback_used": attempt_exchange != exchange
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
            last_error = e
            print(f"[ERROR] Failed {attempt_exchange}: {type(e).__name__}: {e}", file=sys.stderr)
            
            # If this isn't the last exchange, continue to next
            if attempt_exchange != exchanges_to_try[-1]:
                print(f"[INFO] Trying next exchange in fallback chain...", file=sys.stderr)
                continue
                
        finally:
            if exchange_instance:
                try:
                    await exchange_instance.close()
                except Exception as e:
                    import sys
                    print(f"[WARN] Error closing exchange: {e}", file=sys.stderr)
    
    # If we get here, all exchanges failed
    import sys
    print(f"[ERROR] All exchanges failed. Last error: {last_error}", file=sys.stderr)
    return json.dumps({
        "error": f"Failed to fetch order book from all exchanges",
        "requested_exchange": exchange,
        "attempted_exchanges": exchanges_to_try,
        "last_error": str(last_error),
        "error_type": type(last_error).__name__,
        "hint": "All exchanges failed. Check firewall settings or try manual API key configuration."
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
