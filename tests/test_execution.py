"""
Verification Tests for Phase 12 (Execution Engine)
Tests Risk Engine checks and Paper Trading logic.
"""

import sys
import os
import json
import asyncio
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

class MockFastMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

sys.modules["mcp.server.fastmcp"].FastMCP = MockFastMCP

# Mock ccxt, aiosqlite (Need to mock BEFORE importing tools.trading_tools -> tools/__init__ -> exchange_tools)
sys.modules["ccxt"] = MagicMock()
sys.modules["ccxt.async_support"] = MagicMock()
sys.modules["aiosqlite"] = MagicMock()

from tools.trading_tools import register_trading_tools

def test_execution():
    print("\n--- Testing Phase 12: Execution Engine ---")
    mock_mcp = MockFastMCP()
    register_trading_tools(mock_mcp)
    
    execute_order = mock_mcp.tools["execute_order"]
    get_positions = mock_mcp.tools["get_positions"]
    
    # 1. Test Valid BUY (Paper)
    print("Testing Valid BUY...")
    res_buy = json.loads(execute_order("BTC", "BUY", 0.1, 50000.0))
    print(f"Buy Result: {res_buy['status']}")
    
    assert res_buy["status"] == "FILLED"
    assert res_buy["mode"] == "PAPER"
    assert res_buy["quantity"] == 0.1
    print("Valid Buy: PASS")
    
    # 2. Test Risk Rejection (Restricted Asset)
    print("\nTesting Restricted Asset Rejection...")
    res_restricted = json.loads(execute_order("USDT", "BUY", 1000.0, 1.0))
    print(f"Result: {res_restricted['status']} - {res_restricted['reason']}")
    
    assert res_restricted["status"] == "REJECTED"
    assert "restricted" in res_restricted["reason"]
    print("Mask Check: PASS")

    # 3. Test Risk Rejection (Max Size)
    print("\nTesting Max Size Rejection...")
    # $200k > $100k limit
    res_size = json.loads(execute_order("ETH", "BUY", 100.0, 2000.0))
    print(f"Result: {res_size['status']} - {res_size['reason']}")
    
    assert res_size["status"] == "REJECTED"
    assert "exceeds limit" in res_size["reason"]
    print("Max Size Check: PASS")
    
    # 4. Check Positions
    print("\nTesting Position Tracking...")
    res_pos = json.loads(get_positions())
    positions = res_pos["positions"]
    
    print(f"Positions: {positions}")
    assert positions["BTC"] == 0.1
    print("Position Tracking: PASS")

if __name__ == "__main__":
    test_execution()
    print("\nAll Phase 12 Tests Passed!")
