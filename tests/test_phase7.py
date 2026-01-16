"""
Verification Tests for Phase 7 (Exchange Connectivity)
Tests ccxt wrapper tools with mocked exchange responses.
"""

import sys
import os
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp module
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

# Import the tool module (ccxt will be real or ImportError initially, but we patch it)
# We need to handle potential ImportError if ccxt is missing in env, 
# ensuring we can still test the logic by mocking.
try:
    from tools.exchange_tools import register_exchange_tools
except ImportError:
    # If import fails because ccxt missing, we mock it globally first
    sys.modules["ccxt"] = MagicMock()
    sys.modules["ccxt.async_support"] = MagicMock()
    from tools.exchange_tools import register_exchange_tools

class MockFastMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

async def test_exchange_tools():
    print("\n--- Testing Exchange Connectivity Tools ---")
    mock_mcp = MockFastMCP()
    register_exchange_tools(mock_mcp)
    
    tool_book = mock_mcp.tools["fetch_orderbook"]
    tool_ticker = mock_mcp.tools["fetch_ticker"]
    
    # We patch 'tools.exchange_tools.ccxt' to replace the library used in the module
    with patch("tools.exchange_tools.ccxt") as mock_ccxt:
        # Setup Exchange Mock
        mock_exchange = AsyncMock()
        mock_exchange.fetch_order_book.return_value = {
            "bids": [[50000.0, 1.5]],
            "asks": [[50010.0, 1.0]],
            "nonce": 12345,
            "datetime": "2023-01-01T00:00:00Z"
        }
        mock_exchange.fetch_ticker.return_value = {
            "last": 50005.0,
            "high": 51000.0,
            "low": 49000.0,
            "baseVolume": 1000.0,
            "percentage": 1.2
        }
        mock_exchange.close.return_value = None # AsyncMock returns coroutine by default
        
        # Setup ccxt module mock
        mock_ccxt.exchanges = ["binance"]
        # When binance class is instantiated, return mock_exchange
        mock_ccxt.binance.return_value = mock_exchange
        
        # 1. Test fetch_orderbook
        print("Testing fetch_orderbook...")
        result_json = await tool_book("BTC/USDT", "binance", 10)
        result = json.loads(result_json)
        
        if "error" in result:
             print(f"ERROR in tool: {result}")
        
        assert result.get("symbol") == "BTC/USDT"
        assert len(result.get("bids", [])) == 1
        print("fetch_orderbook: PASS")

        # 2. Test fetch_ticker
        print("\nTesting fetch_ticker...")
        result_json = await tool_ticker("BTC/USDT", "binance")
        result = json.loads(result_json)
        
        assert result.get("last_price") == 50005.0
        print("fetch_ticker: PASS")
        
        # 3. Test Invalid Exchange
        print("\nTesting invalid exchange...")
        result_json = await tool_book("BTC/USDT", "invalid_ex")
        result = json.loads(result_json)
        
        assert "error" in result
        print("Invalid exchange handling: PASS")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_exchange_tools())
    print("\nAll Phase 7 Tests Passed!")
