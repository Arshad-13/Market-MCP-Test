"""
Research Agent - Deep Analysis Specialist

Focuses on:
- Fetching market data
- Running ML predictions
- Generating analysis reports
- Identifying trading opportunities
"""

from .base_agent import BaseAgent, AgentContext, AgentDecision, AgentAction
from tools.exchange_tools import fetch_ticker, fetch_orderbook
from tools.strategy_tools import get_trading_signal
import asyncio
import json


class ResearchAgent(BaseAgent):
    """
    Gathers and analyzes market intelligence.
    """
    
    def __init__(self):
        super().__init__("ResearchAgent")
    
    def _run_async(self, coro):
        """Helper to run async functions."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    def think(self, context: AgentContext) -> AgentDecision:
        """
        Fetch data and run analysis.
        """
        try:
            # 1. Fetch ticker data
            ticker_json = self._run_async(fetch_ticker(context.symbol))
            ticker = json.loads(ticker_json)
            
            if "error" in ticker:
                return AgentDecision(
                    agent_name=self.name,
                    action=AgentAction.RESEARCH,
                    confidence=0.0,
                    rationale=f"Failed to fetch ticker: {ticker.get('details', 'Unknown error')}",
                    metadata={"error": ticker}
                )
            
            context.price = ticker.get("last_price")
            
            # 2. Fetch orderbook
            ob_json = self._run_async(fetch_orderbook(context.symbol))
            ob = json.loads(ob_json)
            
            if "error" not in ob:
                context.bids = ob.get("bids", [])
                context.asks = ob.get("asks", [])
            
            # 3. Get trading signal (uses ML + Strategy)
            if context.bids and context.asks:
                signal_json = get_trading_signal(
                    context.symbol,
                    context.bids,
                    context.asks,
                    context.sentiment_score or 50.0
                )
                signal = json.loads(signal_json)
                
                context.ml_prediction = signal.get("ml_signal", {})
                
                # Translate signal to action
                action_map = {
                    "BUY": AgentAction.BUY,
                    "SELL": AgentAction.SELL,
                    "HOLD": AgentAction.HOLD
                }
                action = action_map.get(signal.get("action", "HOLD"), AgentAction.HOLD)
                confidence = signal.get("confidence", 0.0)
                
                # Generate report
                report = self._generate_report(ticker, ob, signal)
                context.research_report = report
                
                return AgentDecision(
                    agent_name=self.name,
                    action=action,
                    confidence=confidence,
                    rationale=signal.get("reason", "Analysis complete"),
                    metadata={
                        "ticker": ticker,
                        "signal": signal,
                        "report_length": len(report)
                    }
                )
            else:
                return AgentDecision(
                    agent_name=self.name,
                    action=AgentAction.RESEARCH,
                    confidence=0.3,
                    rationale="Orderbook data unavailable",
                    metadata={}
                )
                
        except Exception as e:
            return AgentDecision(
                agent_name=self.name,
                action=AgentAction.ALERT,
                confidence=0.0,
                rationale=f"Research failed: {str(e)}",
                metadata={"exception": str(e)}
            )
    
    def _generate_report(self, ticker: dict, orderbook: dict, signal: dict) -> str:
        """Generate a human-readable research report."""
        lines = [
            f"## Research Report: {ticker.get('symbol', 'N/A')}",
            f"**Price:** ${ticker.get('last_price', 0):,.2f}",
            f"**24h Change:** {ticker.get('percentage_change', 0):.2f}%",
            "",
            "### ML Analysis",
            f"- **Signal:** {signal.get('action', 'N/A')}",
            f"- **Confidence:** {signal.get('confidence', 0):.1%}",
            f"- **Reason:** {signal.get('reason', 'N/A')}",
            "",
            "### Orderbook",
            f"- **Top Bid:** ${orderbook.get('bids', [[0]])[0][0]:,.2f}" if orderbook.get('bids') else "- No bids",
            f"- **Top Ask:** ${orderbook.get('asks', [[0]])[0][0]:,.2f}" if orderbook.get('asks') else "- No asks",
        ]
        return "\n".join(lines)
    
    def act(self, decision: AgentDecision, context: AgentContext) -> AgentContext:
        """
        Update context with research findings.
        """
        context.add_message(
            self.name,
            f"Research complete: {decision.action.value} ({decision.confidence:.1%})",
            "INFO"
        )
        return context
