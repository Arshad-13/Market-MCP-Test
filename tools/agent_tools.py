"""
Agent Tools - MCP Interface for Multi-Agent System

Exposes the agent orchestration capabilities via MCP tools.
"""

import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

# NOTE: Lazy import to avoid circular dependency
# from agents.manager_agent import manager


# --- Shared Tools ---

def run_analysis_pipeline(symbol: str, sentiment_score: float = 50.0) -> str:
    """
    Run the full multi-agent analysis pipeline for a symbol.
    
    This triggers:
    1. ResearchAgent: Fetches market data, runs ML analysis
    2. RiskAgent: Assesses portfolio risk
    3. ExecutionAgent: Plans optimal execution
    4. ManagerAgent: Aggregates and provides final recommendation
    
    Args:
        symbol: Trading pair (e.g., "BTC/USDT")
        sentiment_score: Fear & Greed index (0-100). Default 50 (neutral).
        
    Returns:
        JSON with final decision, sub-agent decisions, and research report.
    """
    from agents.manager_agent import manager  # Lazy import
    result = manager.run_pipeline(symbol, sentiment_score)
    return json.dumps(result, default=str)


def get_agent_status() -> str:
    """
    Get the current status of all agents in the system.
    
    Returns:
        JSON with agent names, types, and active status.
    """
    from agents.manager_agent import manager  # Lazy import
    
    agents_info = [
        {
            "name": manager.name,
            "type": "Coordinator",
            "active": manager._is_active,
            "auto_execute": manager.auto_execute
        },
        {
            "name": manager.research_agent.name,
            "type": "Researcher",
            "active": manager.research_agent._is_active
        },
        {
            "name": manager.risk_agent.name,
            "type": "Risk Specialist",
            "active": manager.risk_agent._is_active
        },
        {
            "name": manager.execution_agent.name,
            "type": "Executor",
            "active": manager.execution_agent._is_active
        }
    ]
    
    return json.dumps({
        "total_agents": len(agents_info),
        "agents": agents_info
    })


def set_auto_execute(enabled: bool) -> str:
    """
    Enable or disable automatic trade execution by the agent system.
    
    Args:
        enabled: If True, the ExecutionAgent will actually place trades.
                 If False (default), it will only recommend but not execute.
    
    Returns:
        Confirmation message.
    """
    from agents.manager_agent import manager  # Lazy import
    manager.auto_execute = enabled
    status = "ENABLED" if enabled else "DISABLED"
    return json.dumps({
        "status": "success",
        "message": f"Auto-execution is now {status}",
        "auto_execute": enabled
    })


async def auto_trade(symbol: str, sentiment_score: float = 0.5, position_size: float = 0.01) -> str:
    """
    Autonomous trading: Analyze market and execute trade automatically.
    
    Combines multi-agent analysis with automatic execution.
    Only executes if confidence >= 70%.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        sentiment_score: Market sentiment -1 to 1 (default: 0.5 neutral)
        position_size: Position size as fraction of balance (default: 0.01 = 1%)
    
    Returns:
        JSON with analysis + execution results
    """
    from agents.manager_agent import ManagerAgent
    from tools.trading_tools import execute_order
    from datetime import datetime
    
    try:
        # Run full analysis
        manager = ManagerAgent()
        analysis = await manager.run_pipeline(symbol, sentiment_score)
        
        final_decision = analysis.get("final_decision")
        confidence = analysis.get("confidence", 0)
        
        # Execute if confidence high enough
        execution_result = None
        if confidence >= 0.7:
            if final_decision == "BUY":
                # Get current price from analysis
                current_price = analysis.get("agents", {}).get("research", {}).get("current_price", 0)
                if current_price > 0:
                    execution_result = execute_order(symbol, "buy", position_size, current_price)
                else:
                    execution_result = json.dumps({"status": "error", "reason": "No price data"})
            elif final_decision == "SELL":
                current_price = analysis.get("agents", {}).get("research", {}).get("current_price", 0)
                if current_price > 0:
                    execution_result = execute_order(symbol, "sell", position_size, current_price)
                else:
                    execution_result = json.dumps({"status": "error", "reason": "No price data"})
            else:
                execution_result = json.dumps({"status": "skipped", "reason": "Decision is HOLD"})
        else:
            execution_result = json.dumps({
                "status": "skipped",
                "reason": "Confidence too low",
                "confidence": confidence,
                "threshold": 0.7
            })
        
        return json.dumps({
            "symbol": symbol,
            "analysis": analysis,
            "execution": json.loads(execution_result) if isinstance(execution_result, str) else execution_result,
            "autonomous_mode": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return json.dumps({
            "error": "Auto-trade failed",
            "details": str(e),
            "symbol": symbol
        })


def register_agent_tools(mcp: FastMCP) -> None:
    """
    Register Multi-Agent MCP tools.
    """
    mcp.tool()(run_analysis_pipeline)
    mcp.tool()(get_agent_status)
    mcp.tool()(set_auto_execute)
