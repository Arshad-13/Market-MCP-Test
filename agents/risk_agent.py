"""
Risk Agent - Portfolio Risk Specialist

Focuses on:
- Position sizing
- Exposure limits
- Volatility assessment
- Stop-loss recommendations
"""

from .base_agent import BaseAgent, AgentContext, AgentDecision, AgentAction
from core.risk_engine import risk_engine


class RiskAgent(BaseAgent):
    """
    Analyzes risk factors and recommends position sizing.
    """
    
    def __init__(self):
        super().__init__("RiskAgent")
        self.max_position_pct = 0.10  # Max 10% of capital in one asset
        self.volatility_threshold = 0.05  # 5% vol = high risk
    
    def think(self, context: AgentContext) -> AgentDecision:
        """
        Analyze portfolio risk based on context.
        """
        # Check if we have enough data
        if context.available_capital <= 0:
            return AgentDecision(
                agent_name=self.name,
                action=AgentAction.HOLD,
                confidence=0.9,
                rationale="No capital available for trading",
                metadata={"risk_level": "BLOCKED"}
            )
        
        # Calculate position concentration
        position_value = context.current_position * (context.price or 0)
        concentration = position_value / context.available_capital if context.available_capital > 0 else 0
        
        # Assess risk level
        risk_factors = []
        risk_score = 0.0
        
        # Check concentration risk
        if concentration > self.max_position_pct:
            risk_factors.append(f"Position concentration {concentration:.1%} exceeds {self.max_position_pct:.1%}")
            risk_score += 0.3
            
        # Check sentiment risk (extreme fear or greed)
        if context.sentiment_score is not None:
            if context.sentiment_score < 20:
                risk_factors.append(f"Extreme Fear ({context.sentiment_score})")
                risk_score += 0.2
            elif context.sentiment_score > 80:
                risk_factors.append(f"Extreme Greed ({context.sentiment_score})")
                risk_score += 0.2
                
        # Use core risk engine for pre-trade checks
        if context.price and context.current_position > 0:
            allowed, reason = risk_engine.check_order(
                context.symbol.split('/')[0],  # Extract base asset
                "SELL",
                context.current_position,
                context.price
            )
            if not allowed:
                risk_factors.append(f"RiskEngine: {reason}")
                risk_score += 0.3
        
        # Determine action based on risk
        if risk_score > 0.5:
            action = AgentAction.ALERT
            rationale = f"HIGH RISK: {'; '.join(risk_factors)}"
            confidence = 0.8
        elif risk_score > 0.2:
            action = AgentAction.HOLD
            rationale = f"Moderate risk detected: {'; '.join(risk_factors)}"
            confidence = 0.6
        else:
            action = AgentAction.HOLD  # Risk agent doesn't initiate trades
            rationale = "Risk levels acceptable"
            confidence = 0.9
            
        return AgentDecision(
            agent_name=self.name,
            action=action,
            confidence=confidence,
            rationale=rationale,
            metadata={
                "risk_score": round(risk_score, 2),
                "risk_factors": risk_factors,
                "concentration": round(concentration, 4),
                "max_suggested_position": self.max_position_pct * context.available_capital
            }
        )
    
    def act(self, decision: AgentDecision, context: AgentContext) -> AgentContext:
        """
        Update context with risk assessment.
        """
        context.risk_assessment = decision.metadata
        context.add_message(
            self.name,
            f"{decision.action.value}: {decision.rationale}",
            "WARNING" if decision.action == AgentAction.ALERT else "INFO"
        )
        return context
