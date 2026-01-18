"""
Strategy Tools

MCP tools exposing the Strategy Engine's decision making.
"""

import json
from typing import List
from mcp.server.fastmcp import FastMCP

from core.strategy_engine import strategy_engine

# --- Shared Tools ---

def get_trading_signal(
    symbol: str, 
    bids: List[List[float]], 
    asks: List[List[float]], 
    sentiment_score: float = 50.0
) -> str:
    """
    Get a composite trading signal for an asset.
    
    Combines DeepLOB ML prediction (microstructure) with Sentiment analysis.
    
    Args:
        symbol: Asset symbol (e.g. BTC).
        bids: L2 Orderbook bids [[price, size], ...].
        asks: L2 Orderbook asks.
        sentiment_score: Fear & Greed Index (0-100). Default 50.
        
    Returns:
        JSON signal with Action (BUY/SELL/HOLD) and Rationale.
    """
    signal_data = strategy_engine.generate_signal(symbol, bids, asks, sentiment_score)
    return json.dumps(signal_data)

def register_strategy_tools(mcp: FastMCP) -> None:
    """
    Register Strategy tools.
    """
    mcp.tool()(get_trading_signal)
