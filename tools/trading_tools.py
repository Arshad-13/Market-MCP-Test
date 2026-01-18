"""
Trading Tools (Execution Engine)

MCP tools for executing trades.
Defaults to PAPER TRADING mode for safety.
"""

import json
import logging
import uuid
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

from core.risk_engine import risk_engine

# Configuration
PAPER_TRADING = True
logger = logging.getLogger("TradingTools")

# In-memory paper trading state
_PAPER_POSITIONS: Dict[str, float] = {}
_PAPER_BALANCE = 1000000.0 # $1M paper money

# --- Shared Tools ---

def execute_order(symbol: str, side: str, quantity: float, price: float) -> str:
    """
    Execute a trade order (Buy/Sell).
    
    Args:
        symbol: Asset symbol (e.g. BTC)
        side: "BUY" or "SELL"
        quantity: Amount to trade
        price: Execution price (Limit) or estimated price
        
    Returns:
        JSON execution report.
    """
    global _PAPER_BALANCE
    
    # 1. Risk Check
    allowed, reason = risk_engine.check_order(symbol, side, quantity, price)
    if not allowed:
        return json.dumps({
            "status": "REJECTED",
            "reason": reason,
            "symbol": symbol
        })
        
    # 2. Execution (Paper vs Live)
    trade_value = quantity * price
    
    if PAPER_TRADING:
        # Simulate execution
        order_id = f"paper-{uuid.uuid4().hex[:8]}"
        
        if side.upper() == "BUY":
            if _PAPER_BALANCE < trade_value:
                return json.dumps({"status": "REJECTED", "reason": "Insufficient paper funds"})
            _PAPER_BALANCE -= trade_value
            _PAPER_POSITIONS[symbol] = _PAPER_POSITIONS.get(symbol, 0.0) + quantity
        
        elif side.upper() == "SELL":
            current_qty = _PAPER_POSITIONS.get(symbol, 0.0)
            if current_qty < quantity:
                return json.dumps({"status": "REJECTED", "reason": "Insufficient position"})
            _PAPER_BALANCE += trade_value
            _PAPER_POSITIONS[symbol] = current_qty - quantity
        
        return json.dumps({
            "status": "FILLED",
            "mode": "PAPER",
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
            "value": trade_value,
            "remaining_balance": _PAPER_BALANCE
        })
    else:
        # Real execution would go here (using exchange_tools/ccxt private api)
        pass
        
    return json.dumps({"status": "ERROR", "message": "Live trading not fully implemented yet"})

def get_positions() -> str:
    """
    Get current portfolio positions.
    """
    if PAPER_TRADING:
        return json.dumps({
            "mode": "PAPER",
            "balance_usd": _PAPER_BALANCE,
            "positions": _PAPER_POSITIONS
        })
    else:
        return json.dumps({"status": "ERROR", "message": "Live positioning not implemented"})

def register_trading_tools(mcp: FastMCP) -> None:
    """
    Register Trading/Execution tools.
    """
    mcp.tool()(execute_order)
    mcp.tool()(get_positions)
