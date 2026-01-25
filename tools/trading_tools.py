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


def get_balance() -> str:
    """
    Get current account balance.
    
    Returns:
        JSON with balance information
    """
    global _PAPER_BALANCE
    
    return json.dumps({
        "mode": "PAPER",
        "balance_usd": _PAPER_BALANCE,
        "initial_balance": 1000000.0,
        "profit_loss": _PAPER_BALANCE - 1000000.0,
        "profit_loss_pct": ((_PAPER_BALANCE - 1000000.0) / 1000000.0) * 100
    })


def reset_balance() -> str:
    """
    Reset paper trading balance to initial $1M.
    
    Clears all positions and resets capital.
    
    Returns:
        Confirmation message
    """
    global _PAPER_BALANCE, _PAPER_POSITIONS
    
    _PAPER_BALANCE = 1000000.0
    _PAPER_POSITIONS = {}
    
    return json.dumps({
        "status": "success",
        "message": "Paper trading account reset",
        "balance_usd": _PAPER_BALANCE,
        "positions": {}
    })


def set_balance(amount: float) -> str:
    """
    Set paper trading balance to a specific amount.
    
    Args:
        amount: New balance amount in USD
        
    Returns:
        Confirmation message
    """
    global _PAPER_BALANCE
    
    if amount <= 0:
        return json.dumps({
            "status": "error",
            "message": "Balance must be greater than 0"
        })
    
    old_balance = _PAPER_BALANCE
    _PAPER_BALANCE = amount
    
    return json.dumps({
        "status": "success",
        "message": f"Balance updated from ${old_balance:,.2f} to ${amount:,.2f}",
        "old_balance": old_balance,
        "new_balance": _PAPER_BALANCE
    })


def get_pnl_report() -> str:
    """
    Generate comprehensive profit/loss report.
    
    Shows:
    - Current balance vs initial
    - Total P&L
    - All positions with unrealized P&L
    - Trade history summary
    
    Returns:
        JSON with complete P&L analysis
    """
    global _PAPER_BALANCE, _PAPER_POSITIONS
    
    initial_balance = 1000000.0
    current_balance = _PAPER_BALANCE
    realized_pnl = current_balance - initial_balance
    
    # Calculate position values (simplified - uses entry price as current for now)
    position_details = []
    for symbol, quantity in _PAPER_POSITIONS.items():
        if quantity > 0:
            position_details.append({
                "symbol": symbol,
                "quantity": quantity,
                "note": "Use fetch_ticker to get current value"
            })
    
    return json.dumps({
        "summary": {
            "initial_balance": initial_balance,
            "current_balance": current_balance,
            "realized_pnl": realized_pnl,
            "realized_pnl_pct": (realized_pnl / initial_balance) * 100,
            "total_positions": len([p for p in _PAPER_POSITIONS.values() if p > 0])
        },
        "positions": position_details,
        "balance_history": {
            "start": initial_balance,
            "current": current_balance,
            "change": realized_pnl
        },
        "mode": "PAPER_TRADING"
    })


def register_trading_tools(mcp: FastMCP) -> None:
    """
    Register Trading/Execution tools.
    """
    mcp.tool()(execute_order)
    mcp.tool()(get_positions)
    mcp.tool()(get_balance)
    mcp.tool()(reset_balance)
    mcp.tool()(set_balance)
    mcp.tool()(get_pnl_report)
