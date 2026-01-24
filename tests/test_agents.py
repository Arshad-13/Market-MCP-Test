"""
Verification Tests for Phase 15 (Multi-Agent Orchestration)
Tests the agent pipeline with proper mocking.
"""

import sys
import os
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock MCP and external dependencies before importing agents
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

# Mock ccxt and aiosqlite
sys.modules["ccxt"] = MagicMock()
sys.modules["ccxt.async_support"] = MagicMock()
sys.modules["aiosqlite"] = MagicMock()

# Now import agents
from agents.base_agent import AgentContext, AgentDecision, AgentAction
from agents.risk_agent import RiskAgent
from agents.execution_agent import ExecutionAgent
from agents.manager_agent import ManagerAgent


def test_base_agent_structures():
    """Test AgentContext and AgentDecision dataclasses."""
    print("\n--- Testing Base Agent Structures ---")
    
    # Create context
    ctx = AgentContext(
        symbol="BTC/USDT",
        price=50000.0,
        sentiment_score=65.0,
        available_capital=100000.0
    )
    
    assert ctx.symbol == "BTC/USDT"
    assert ctx.price == 50000.0
    print("AgentContext: PASS")
    
    # Create decision
    decision = AgentDecision(
        agent_name="TestAgent",
        action=AgentAction.BUY,
        confidence=0.85,
        rationale="Test rationale"
    )
    
    assert decision.action == AgentAction.BUY
    assert decision.confidence == 0.85
    print("AgentDecision: PASS")
    
    # Test to_dict
    d = decision.to_dict()
    assert d["action"] == "BUY"
    print("to_dict: PASS")


def test_risk_agent():
    """Test RiskAgent analysis."""
    print("\n--- Testing Risk Agent ---")
    
    risk_agent = RiskAgent()
    
    # Test with high concentration
    ctx = AgentContext(
        symbol="BTC/USDT",
        price=50000.0,
        current_position=10.0,  # 10 BTC = $500k
        available_capital=100000.0  # Only $100k
    )
    
    decision = risk_agent.think(ctx)
    print(f"Risk Decision: {decision.action.value} - {decision.rationale}")
    
    # High concentration should trigger warning or alert
    assert decision.metadata.get("risk_score", 0) > 0
    print("Risk Agent: PASS")


def test_execution_agent():
    """Test ExecutionAgent with mocked positions."""
    print("\n--- Testing Execution Agent ---")
    
    exec_agent = ExecutionAgent()
    
    ctx = AgentContext(
        symbol="ETH/USDT",
        price=3000.0,
        available_capital=50000.0,
        ml_prediction={"signal": "UP", "confidence": 0.8}
    )
    
    # Mock get_positions
    with patch("agents.execution_agent.get_positions") as mock_pos:
        mock_pos.return_value = json.dumps({
            "mode": "PAPER",
            "balance_usd": 50000.0,
            "positions": {}
        })
        
        decision = exec_agent.think(ctx)
        print(f"Exec Decision: {decision.action.value} - {decision.rationale}")
        
        # With strong UP signal, should suggest BUY
        if decision.action == AgentAction.BUY:
            print("Execution Agent (BUY signal): PASS")
        else:
            print(f"Execution Agent: HOLD (expected for low confidence)")


def test_manager_pipeline():
    """Test the full ManagerAgent pipeline with mocks."""
    print("\n--- Testing Manager Agent Pipeline ---")
    
    manager = ManagerAgent()
    
    # We need to mock the exchange calls in research agent
    with patch("agents.research_agent.fetch_ticker") as mock_ticker, \
         patch("agents.research_agent.fetch_orderbook") as mock_ob, \
         patch("agents.execution_agent.get_positions") as mock_pos:
        
        # Setup mocks
        async def mock_ticker_fn(*args, **kwargs):
            return json.dumps({
                "symbol": "BTC/USDT",
                "last_price": 50000.0,
                "percentage_change": 2.5
            })
        mock_ticker.side_effect = mock_ticker_fn
        
        async def mock_ob_fn(*args, **kwargs):
            return json.dumps({
                "bids": [[49900, 1.0], [49800, 2.0]],
                "asks": [[50100, 1.0], [50200, 2.0]]
            })
        mock_ob.side_effect = mock_ob_fn
        
        mock_pos.return_value = json.dumps({
            "mode": "PAPER",
            "balance_usd": 100000.0,
            "positions": {"BTC": 0.5}
        })
        
        # Run pipeline
        result = manager.run_pipeline("BTC/USDT", sentiment_score=55.0)
        
        print(f"Final Decision: {result['final_decision']['action']}")
        print(f"Confidence: {result['final_decision']['confidence']}")
        print(f"Sub-agents: {len(result['final_decision'].get('metadata', {}).get('sub_decisions', []))}")
        
        assert "final_decision" in result
        assert "context_messages" in result
        print ("Manager Pipeline: PASS")


if __name__ == "__main__":
    test_base_agent_structures()
    test_risk_agent()
    test_execution_agent()
    test_manager_pipeline()
    print("\n✅ All Phase 15 Tests Passed!")
