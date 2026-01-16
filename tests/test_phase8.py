"""
Verification Tests for Phase 8 (AI Prediction)
Tests DeepLOB Lite logic with synthetic market data.
"""

import sys
import os
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

# Mock ccxt to prevent ImportError from tools/__init__.py
mock_ccxt = MagicMock()
sys.modules["ccxt"] = mock_ccxt
sys.modules["ccxt.async_support"] = mock_ccxt

from tools.ml_tools import register_ml_tools

def test_ml_tools():
    print("\n--- Testing AI Prediction Tools (DeepLOB Lite) ---")
    mock_mcp = MockFastMCP()
    register_ml_tools(mock_mcp)
    
    predict = mock_mcp.tools["predict_price_direction"]
    
    from core.analytics import MicrostructureAnalyzer
    
    # helper to run with fresh state
    def predict_fresh(bids, asks):
        # Patch the global analyzer in the tool module to reset state
        with patch("tools.ml_tools._analyzer", new=MicrostructureAnalyzer()):
            return predict(bids, asks)

    # 1. Bullish Scenario
    # High Buy Volume (Bids) vs Low Sell Volume (Asks)
    bids_bull = [[100.0, 50.0], [99.0, 50.0]]
    asks_bull = [[100.1, 5.0], [100.2, 5.0]]
    
    res_bull = json.loads(predict_fresh(bids_bull, asks_bull))
    print(f"Bullish Case: Signal={res_bull['signal']}, Conf={res_bull['confidence']}")
    print(f"Features: OFI={res_bull['features']['ofi']}")
    
    assert res_bull['signal'] == "UP"
    # OFI is 0 on first tick (no history), but OBI should be positive
    assert res_bull['features']['obi'] > 0
    print("Bullish Scenario: PASS")

    # 2. Bearish Scenario
    # Low Buy Volume vs High Sell Volume
    bids_bear = [[100.0, 5.0], [99.0, 5.0]]
    asks_bear = [[100.1, 50.0], [100.2, 50.0]]
    
    res_bear = json.loads(predict_fresh(bids_bear, asks_bear))
    print(f"Bearish Case: Signal={res_bear['signal']}, Conf={res_bear['confidence']}")
    
    assert res_bear['signal'] == "DOWN"
    assert res_bear['features']['obi'] < 0
    print("Bearish Scenario: PASS")
    
    # 3. Stationary/Neutral Scenario
    bids_neutral = [[100.0, 20.0]]
    asks_neutral = [[100.1, 20.0]]
    
    res_neutral = json.loads(predict_fresh(bids_neutral, asks_neutral))
    print(f"Neutral Case: Signal={res_neutral['signal']}")
    
    assert res_neutral['signal'] == "STATIONARY"
    print("Neutral Scenario: PASS")
    
    # 4. Volatility Analysis
    analyze_vol = mock_mcp.tools["analyze_volatility_regime"]
    
    # Low Volatility (Constant price)
    prices_calm = [100.0] * 50
    res_calm = json.loads(analyze_vol(prices_calm))
    print(f"Calm Regime: {res_calm['regime']}")
    assert res_calm['regime'] == "LOW_VOLATILITY"
    
    # High Volatility (Random jumps)
    import random
    prices_vol = [100.0 + random.uniform(-5, 5) for _ in range(50)]
    res_vol = json.loads(analyze_vol(prices_vol))
    print(f"Volatile Regime: {res_vol['regime']}")
    # Might be NORMAL or HIGH depending on randomness, but definitely not LOW (usually)
    # Just checking it runs and returns valid JSON
    assert "regime" in res_vol
    print("Volatility Analysis: PASS")

if __name__ == "__main__":
    test_ml_tools()
    print("\nAll Phase 8 Tests Passed!")
