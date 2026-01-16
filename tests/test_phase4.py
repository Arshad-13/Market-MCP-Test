"""
Verification Tests for Phase 4 (External APIs)
Tests Sentiment and DeFi tools with mocked API responses.
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

class MockFastMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

sys.modules["mcp.server.fastmcp"].FastMCP = MockFastMCP

from tools.sentiment_tools import register_sentiment_tools
from tools.defi_tools import register_defi_tools

async def test_sentiment_tools():
    print("\n--- Testing Sentiment Tools ---")
    mock_mcp = MockFastMCP()
    register_sentiment_tools(mock_mcp)
    
    tool = mock_mcp.tools["get_fear_and_greed_index"]
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{
            "value": "20",
            "value_classification": "Extreme Fear",
            "timestamp": "1700000000"
        }]
    }
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result_json = await tool()
        result = json.loads(result_json)
        
        print(f"F&G Value: {result.get('value')}")
        print(f"Classification: {result.get('classification')}")
        
        assert result["value"] == 20
        assert result["classification"] == "Extreme Fear"
        assert "interpretation" in result
        print("Sentiment Tools: PASS")

async def test_defi_tools():
    print("\n--- Testing DeFi Tools ---")
    mock_mcp = MockFastMCP()
    register_defi_tools(mock_mcp)
    
    # Test 1: Global Stats
    tool_global = mock_mcp.tools["get_defi_global_stats"]
    
    mock_chains_response = MagicMock()
    mock_chains_response.json.return_value = [
        {"name": "Ethereum", "tvl": 50000000000, "tokenSymbol": "ETH"},
        {"name": "Solana", "tvl": 4000000000, "tokenSymbol": "SOL"}
    ]
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_chains_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result_json = await tool_global()
        result = json.loads(result_json)
        
        print(f"Total TVL: {result.get('total_tvl_usd')}")
        print(f"Top Chains: {len(result.get('top_chains'))}")
        
        assert result["total_tvl_usd"] == 54000000000
        assert result["top_chains"][0]["name"] == "Ethereum"
        print("DeFi Global Stats: PASS")

    # Test 2: Gas Tracker (No API Key)
    tool_gas = mock_mcp.tools["get_gas_price"]
    
    # We expect an error or fallback message if key is missing
    # Assuming ENV var is not set in test environment
    result_json = await tool_gas()
    result = json.loads(result_json)
    
    print(f"Gas Tool Result: {result}")
    assert "error" in result # "ETHERSCAN_API_KEY not set"
    print("DeFi Gas Tracker (No Key): PASS")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_sentiment_tools())
    loop.run_until_complete(test_defi_tools())
    print("\nAll Phase 4 Tests Passed!")
