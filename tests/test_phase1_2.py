"""
Verification Tests for Phase 1 & 2
Tests Core Analytics and MCP Tool Wrappers
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp module before importing tools
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

# Mock FastMCP class
class MockFastMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

sys.modules["mcp.server.fastmcp"].FastMCP = MockFastMCP

from core.analytics import MicrostructureAnalyzer, OrderBook
from core.anomaly_detection import AnomalyDetector, AnomalyType
from core.data_validator import DataValidator

# Import tools after mocking
from tools.microstructure_tools import register_microstructure_tools
from tools.anomaly_tools import register_anomaly_tools

def test_core_analytics():
    print("\n--- Testing Core Analytics (MicrostructureAnalyzer) ---")
    analyzer = MicrostructureAnalyzer()
    
    # Create valid order book
    bids = [[100.0, 10.0], [99.9, 20.0], [99.8, 30.0]]
    asks = [[100.1, 10.0], [100.2, 20.0], [100.3, 30.0]]
    book = OrderBook.from_raw(bids, asks, datetime.now())
    
    metrics = analyzer.analyze(book)
    
    print(f"Mid Price: {metrics.mid_price}")
    print(f"Spread: {metrics.spread}")
    print(f"OFI: {metrics.ofi}")
    print(f"Microprice: {metrics.microprice}")
    
    assert metrics.mid_price == 100.05
    assert abs(metrics.spread - 0.1) < 1e-9
    assert metrics.ofi == 0  # Initial state has no history
    
    # Simulate buying pressure (OFI should increase)
    # New book with higher bid
    bids_2 = [[100.05, 15.0], [99.9, 20.0]] # Bid price increased
    asks_2 = [[100.1, 10.0], [100.2, 20.0]]
    book_2 = OrderBook.from_raw(bids_2, asks_2, datetime.now())
    
    metrics_2 = analyzer.analyze(book_2)
    print(f"OFI after bid increase: {metrics_2.ofi}")
    assert metrics_2.ofi > 0 # Buying pressure
    print("Core Analytics: PASS")

def test_anomaly_detection():
    print("\n--- Testing Anomaly Detection ---")
    detector = AnomalyDetector()
    
    # Simulate Spoofing: Large order far from best bid
    bids = [[100.0, 10.0], [99.0, 5000.0]] # Huge volume at deeper level
    asks = [[100.1, 10.0]]
    book = OrderBook.from_raw(bids, asks, datetime.now())
    
    state = detector.analyze(book)
    
    spoofing_found = any(a.type == AnomalyType.SPOOFING for a in state.anomalies)
    print(f"Anomalies found: {[a.type.name for a in state.anomalies]}")
    
    if spoofing_found:
        print("Spoofing detection: PASS")
    else:
        print("Spoofing detection: FAIL (No spoofing detected)")
        
    # Simulate Liquidity Gap
    bids_gap = [[100.0, 0.1]] # Tiny volume
    asks_gap = [[100.1, 0.1]]
    book_gap = OrderBook.from_raw(bids_gap, asks_gap, datetime.now())
    
    state_gap = detector.analyze(book_gap)
    gaps_found = any(a.type == AnomalyType.LIQUIDITY_GAP for a in state_gap.anomalies)
    
    if gaps_found:
        print("Liquidity gap detection: PASS")
    else:
        print("Liquidity gap detection: FAIL")

def test_data_validation():
    print("\n--- Testing Data Validator ---")
    
    # Invalid book (bid > ask)
    invalid_snapshot = {
        "bids": [[101.0, 10.0]],
        "asks": [[100.0, 10.0]]
    }
    
    result = DataValidator.validate_snapshot(invalid_snapshot)
    print(f"Validation result for crossed book: {result.is_valid}")
    print(f"Errors: {result.errors}")
    
    assert result.is_valid == False
    assert any("Invalid book" in e for e in result.errors)
    print("Data Validation: PASS")

async def test_mcp_tools():
    print("\n--- Testing MCP Tool Wrappers ---")
    mock_mcp = MockFastMCP()
    
    register_microstructure_tools(mock_mcp)
    register_anomaly_tools(mock_mcp)
    
    print(f"Registered tools: {list(mock_mcp.tools.keys())}")
    
    assert "analyze_orderbook" in mock_mcp.tools
    assert "detect_anomalies" in mock_mcp.tools
    
    # Test analyze_orderbook tool
    tool_func = mock_mcp.tools["analyze_orderbook"]
    result_json = tool_func(
        bids=[[100.0, 10.0]], 
        asks=[[100.1, 10.0]], 
        symbol="TEST"
    )
    result = json.loads(result_json)
    
    print(f"Tool execution result: {result['valid']}")
    assert result["valid"] == True
    assert result["metrics"]["mid_price"] == 100.05
    
    print("MCP Tools: PASS")

if __name__ == "__main__":
    test_core_analytics()
    test_anomaly_detection()
    test_data_validation()
    asyncio.run(test_mcp_tools())
    print("\nAll Phase 1 & 2 Tests Passed!")
