"""
Integration Test for Market Server
Verifies that the server module loads and registers all tools/prompts correctly.
"""

import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp module fully to intercept tool registration
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

class MockFastMCP:
    def __init__(self, name):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.prompts = {}
    
    def tool(self, name=None):
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return decorator
        
    def resource(self, uri):
        def decorator(func):
            self.resources[uri] = func
            return func
        return decorator

    def prompt(self, name=None):
        def decorator(func):
            prompt_name = name or func.__name__
            self.prompts[prompt_name] = func
            return func
        return decorator
        
    def run(self):
        print("Mock Server Running")

sys.modules["mcp.server.fastmcp"].FastMCP = MockFastMCP

# Import the server module (which runs registration logic on import)
import market_server

def test_server_integration():
    print("\n--- Testing Server Integration ---")
    server = market_server.mcp
    
    print(f"Server Name: {server.name}")
    print(f"Registered Tools: {len(server.tools)}")
    print(f"Registered Prompts: {len(server.prompts)}")
    print(f"Registered Resources: {len(server.resources)}")
    
    # Check essential tools
    expected_tools = [
        "get_crypto_price",
        "analyze_orderbook", 
        "detect_anomalies",
        "get_fear_and_greed_index",
        "get_defi_global_stats"
    ]
    
    for tool in expected_tools:
        assert tool in server.tools
        print(f"Verified tool: {tool}")
        
    # Check prompts
    expected_prompts = [
        "daily_briefing",
        "hunt_anomalies"
    ]
    
    for prompt in expected_prompts:
        assert prompt in server.prompts
        print(f"Verified prompt: {prompt}")
        
    print("Integration Test: PASS")

if __name__ == "__main__":
    test_server_integration()
