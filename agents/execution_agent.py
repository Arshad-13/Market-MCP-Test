"""
Execution Agent - Smart Order Routing Specialist

Focuses on:
- Order type selection (Market/Limit)
- Slippage optimization
- Execution timing
- Position building/unwinding strategies
"""

from .base_agent import BaseAgent, AgentContext, AgentDecision, AgentAction
from tools.trading_tools import execute_order, get_positions
import json


class ExecutionAgent(BaseAgent):
    """
    Handles intelligent order execution.
    """
    
    def __init__(self):
        super().__init__("ExecutionAgent")
        self.min_confidence_to_execute = 0.7  # Only execute if > 70% confident
    
    def think(self, context: AgentContext) -> AgentDecision:
        """
        Analyze if and how to execute based on context.
        """
        # Get current positions
        pos_data = json.loads(get_positions())
        balance = pos_data.get("balance_usd", 0)
        positions = pos_data.get("positions", {})
        
        # Update context with live data
        context.available_capital = balance
        asset = context.symbol.split('/')[0] if '/' in context.symbol else context.symbol
        context.current_position = positions.get(asset, 0)
        
        # Check ML prediction from context
        ml_pred = context.ml_prediction or {}
        ml_signal = ml_pred.get("signal", "STATIONARY")
        ml_confidence = ml_pred.get("confidence", 0.0)
        
        # Check risk assessment
        risk_data = context.risk_assessment or {}
        risk_score = risk_data.get("risk_score", 0)
        
        # Decision logic
        if risk_score > 0.5:
            return AgentDecision(
                agent_name=self.name,
                action=AgentAction.HOLD,
                confidence=0.9,
                rationale="Risk too high for execution",
                metadata={"blocked_by": "risk"}
            )
        
        if ml_signal == "UP" and ml_confidence >= self.min_confidence_to_execute:
            # Calculate position size (simplified: 5% of capital)
            trade_value = balance * 0.05
            quantity = trade_value / context.price if context.price else 0
            
            return AgentDecision(
                agent_name=self.name,
                action=AgentAction.BUY,
                confidence=ml_confidence,
                rationale=f"ML Bullish ({ml_confidence:.1%}), Risk OK",
                metadata={
                    "order_type": "LIMIT",
                    "quantity": round(quantity, 6),
                    "price": context.price,
                    "trade_value": round(trade_value, 2)
                }
            )
            
        elif ml_signal == "DOWN" and ml_confidence >= self.min_confidence_to_execute:
            # Sell existing position if any
            if context.current_position > 0:
                return AgentDecision(
                    agent_name=self.name,
                    action=AgentAction.SELL,
                    confidence=ml_confidence,
                    rationale=f"ML Bearish ({ml_confidence:.1%}), Closing position",
                    metadata={
                        "order_type": "MARKET",
                        "quantity": context.current_position,
                        "price": context.price
                    }
                )
        
        return AgentDecision(
            agent_name=self.name,
            action=AgentAction.HOLD,
            confidence=0.5,
            rationale="No clear execution signal",
            metadata={}
        )
    
    def act(self, decision: AgentDecision, context: AgentContext) -> AgentContext:
        """
        Execute the order if action is BUY/SELL.
        """
        if decision.action in [AgentAction.BUY, AgentAction.SELL]:
            meta = decision.metadata
            asset = context.symbol.split('/')[0] if '/' in context.symbol else context.symbol
            
            result_json = execute_order(
                symbol=asset,
                side=decision.action.value,
                quantity=meta.get("quantity", 0),
                price=meta.get("price", 0)
            )
            result = json.loads(result_json)
            
            context.add_message(
                self.name,
                f"Executed {decision.action.value}: {result.get('status')} - {result.get('order_id', 'N/A')}",
                "INFO" if result.get("status") == "FILLED" else "WARNING"
            )
        else:
            context.add_message(
                self.name,
                f"No execution: {decision.rationale}",
                "INFO"
            )
        
        return context
