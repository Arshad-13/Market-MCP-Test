"""
Streaming Tools for WebSocket Market Data

MCP tools for real-time market data streaming via WebSocket connections.
"""

import json
from mcp.server.fastmcp import FastMCP


# Module-level functions (accessible by dashboard and MCP)

async def subscribe_stream(
    symbol: str,
    stream_type: str = "orderbook",
    exchange: str = "binance"
) -> str:
    """
    Subscribe to a real-time WebSocket stream.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        stream_type: 'orderbook' or 'ticker'
        exchange: Exchange name (default: 'binance')
        
    Returns:
        JSON with stream_id and status
    """
    from core.websocket_manager import ws_manager
    
    try:
        # Simple callback that stores latest data
        latest_data = {}
        
        def callback(data):
            latest_data.update(data)
        
        if stream_type == "orderbook":
            stream_id = await ws_manager.subscribe_binance_orderbook(symbol, callback)
        elif stream_type == "ticker":
            stream_id = await ws_manager.subscribe_binance_ticker(symbol, callback)
        else:
            return json.dumps({
                "error": f"Invalid stream_type: {stream_type}",
                "valid_types": ["orderbook", "ticker"]
            })
        
        return json.dumps({
            "stream_id": stream_id,
            "symbol": symbol,
            "exchange": exchange,
            "type": stream_type,
            "status": "subscribed",
            "message": f"Successfully subscribed to {stream_type} stream for {symbol}"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to subscribe to stream: {str(e)}",
            "symbol": symbol,
            "exchange": exchange
        })


async def unsubscribe_stream(stream_id: str) -> str:
    """
    Unsubscribe from a WebSocket stream.
    
    Args:
        stream_id: Stream identifier to close
        
    Returns:
        JSON with status
    """
    from core.websocket_manager import ws_manager
    
    try:
        await ws_manager.unsubscribe(stream_id)
        
        return json.dumps({
            "stream_id": stream_id,
            "status": "unsubscribed",
            "message": f"Successfully unsubscribed from {stream_id}"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to unsubscribe: {str(e)}",
            "stream_id": stream_id
        })


def get_active_streams() -> str:
    """
    Get status of all active WebSocket streams.
    
    Returns:
        JSON with all active streams and their statuses
    """
    from core.websocket_manager import ws_manager
    
    try:
        streams = ws_manager.get_active_streams()
        
        return json.dumps({
            "active_streams": streams,
            "total_count": len(streams),
            "timestamp": json.dumps(None)  # Will be replaced with current time
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get active streams: {str(e)}"
        })


def get_stream_status(stream_id: str) -> str:
    """
    Get status of a specific WebSocket stream.
    
    Args:
        stream_id: Stream identifier
        
    Returns:
        JSON with stream status
    """
    from core.websocket_manager import ws_manager
    
    try:
        status = ws_manager.get_stream_status(stream_id)
        
        if status is None:
            return json.dumps({
                "error": f"Stream not found: {stream_id}",
                "stream_id": stream_id
            })
        
        return json.dumps(status)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get stream status: {str(e)}",
            "stream_id": stream_id
        })


# MCP Tool Registration

def register_streaming_tools(mcp: FastMCP):
    """Register WebSocket streaming tools with the MCP server."""
    
    @mcp.tool()
    async def subscribe_orderbook_stream(symbol: str, exchange: str = "binance") -> str:
        """
        Subscribe to a real-time orderbook WebSocket stream.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            exchange: Exchange name (default: 'binance')
        """
        return await subscribe_stream(symbol, "orderbook", exchange)
    
    @mcp.tool()
    async def subscribe_ticker_stream(symbol: str, exchange: str = "binance") -> str:
        """
        Subscribe to a real-time ticker WebSocket stream.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            exchange: Exchange name (default: 'binance')
        """
        return await subscribe_stream(symbol, "ticker", exchange)
    
    @mcp.tool()
    async def stop_stream(stream_id: str) -> str:
        """
        Stop a WebSocket stream.
        
        Args:
            stream_id: Stream identifier returned from subscribe
        """
        return await unsubscribe_stream(stream_id)
    
    @mcp.tool()
    def list_active_streams() -> str:
        """
        List all active WebSocket streams with their statuses.
        """
        return get_active_streams()
    
    @mcp.tool()
    def check_stream_health(stream_id: str) -> str:
        """
        Check the health and status of a specific stream.
        
        Args:
            stream_id: Stream identifier
        """
        return get_stream_status(stream_id)
