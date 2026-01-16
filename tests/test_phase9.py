"""
Verification Tests for Phase 9 (Portfolio Intelligence)
Tests risk analysis and slippage simulation tools.
"""

import sys
import os
import json
from unittest.mock import MagicMock

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

# Mock ccxt to prevent ImportError from tools/__init__.py
mock_ccxt = MagicMock()
sys.modules["ccxt"] = mock_ccxt
sys.modules["ccxt.async_support"] = mock_ccxt

from tools.portfolio_tools import register_portfolio_tools

def test_portfolio_tools():
    print("\n--- Testing Portfolio & Risk Tools ---")
    mock_mcp = MockFastMCP()
    register_portfolio_tools(mock_mcp)
    
    analyze_risk = mock_mcp.tools["analyze_portfolio_risk"]
    sim_slippage = mock_mcp.tools["simulate_slippage"]
    
    # 1. Test Portfolio Risk Analysis
    print("Testing analyze_portfolio_risk...")
    
    # Risky Portfolio (Concentrated in Memecoin)
    holdings_risky = [
        {"symbol": "PEPE", "amount": 1000000, "price_usd": 0.00001} # $10 Value, 100% concentration
    ]
    # Wait, let's make it 100% concentrated to trigger High Concentration Risk
    res_risky = json.loads(analyze_risk(holdings_risky))
    print(f"Risky Portfolio: Score={res_risky['risk_score_0_to_100']}, Level={res_risky['risk_level']}")
    
    assert res_risky['components']['concentration_risk'] > 90 # 100% conc
    assert res_risky['risk_score_0_to_100'] > 50
    print("Risky Portfolio: PASS")
    
    # Balanced Portfolio
    holdings_safe = [
        {"symbol": "USDT", "amount": 5000, "price_usd": 1.0},
        {"symbol": "USDC", "amount": 5000, "price_usd": 1.0}
    ]
    res_safe = json.loads(analyze_risk(holdings_safe))
    print(f"Safe Portfolio: Score={res_safe['risk_score_0_to_100']}, Level={res_safe['risk_level']}")
    
    assert res_safe['risk_score_0_to_100'] < 40 # Stablecoins have low vol
    print("Safe Portfolio: PASS")

    # 2. Test Slippage Simulation
    print("\nTesting simulate_slippage...")
    
    # Small trade (negligible impact)
    res_small = json.loads(sim_slippage("BTC", 100.0, 1000000.0))
    print(f"Small Trade Impact: {res_small['estimated_slippage_pct']}%")
    assert res_small['estimated_slippage_pct'] <= 0.01
    
    # Whale trade (huge impact)
    # Trade Size = 5x Liquidity ($5M) -> ratio 5.0 -> 0.5 * (5.0)^0.6 
    # 5^0.6 ≈ 2.62 -> impact ≈ 1.31% -> "Moderate Slippage"
    res_whale = json.loads(sim_slippage("BTC", 5000000.0, 1000000.0))
    print(f"Whale Trade Impact: {res_whale['estimated_slippage_pct']}%")
    
    assert res_whale['estimated_slippage_pct'] > 1.0
    assert res_whale['warning_level'] != "Safe"
    print("Slippage Simulation: PASS")

if __name__ == "__main__":
    test_portfolio_tools()
    print("\nAll Phase 9 Tests Passed!")
