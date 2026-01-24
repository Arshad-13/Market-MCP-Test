"""
Manager Agent - The Coordinator

Orchestrates the multi-agent pipeline:
1. Research Agent -> Gather data
2. Risk Agent -> Assess risk
3. Execution Agent -> Execute if appropriate

Aggregates decisions and provides final recommendation.
"""

from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentContext, AgentDecision, AgentAction
from .research_agent import ResearchAgent
from .risk_agent import RiskAgent
from .execution_agent import ExecutionAgent


class ManagerAgent(BaseAgent):
    """
    Coordinates multiple specialized agents in a pipeline.
    """
    
    def __init__(self):
        super().__init__("ManagerAgent")
        
        # Initialize sub-agents
        self.research_agent = ResearchAgent()
        self.risk_agent = RiskAgent()
        self.execution_agent = ExecutionAgent()
        
        # Pipeline configuration
        self.auto_execute = False  # If True, execution agent will trade
    
    def think(self, context: AgentContext) -> AgentDecision:
        """
        Run the full analysis pipeline and aggregate results.
        """
        decisions: List[AgentDecision] = []
        
        # Stage 1: Research
        context = self.research_agent.run(context)
        decisions.append(self.research_agent.think(context))
        
        # Stage 2: Risk Assessment
        context = self.risk_agent.run(context)
        decisions.append(self.risk_agent.think(context))
        
        # Stage 3: Execution Planning (but not executing yet)
        exec_decision = self.execution_agent.think(context)
        decisions.append(exec_decision)
        
        # Aggregate decisions
        return self._aggregate_decisions(decisions, context)
    
    def _aggregate_decisions(self, decisions: List[AgentDecision], context: AgentContext) -> AgentDecision:
        """
        Combine multiple agent decisions into a final recommendation.
        """
        # Voting weights by agent
        weights = {
            "ResearchAgent": 0.4,
            "RiskAgent": 0.3,
            "ExecutionAgent": 0.3
        }
        
        # Collect votes
        action_scores = {
            AgentAction.BUY: 0.0,
            AgentAction.SELL: 0.0,
            AgentAction.HOLD: 0.0,
            AgentAction.ALERT: 0.0,
            AgentAction.RESEARCH: 0.0
        }
        
        for decision in decisions:
            weight = weights.get(decision.agent_name, 0.2)
            action_scores[decision.action] += decision.confidence * weight
        
        # Find winning action
        best_action = max(action_scores, key=action_scores.get)
        best_score = action_scores[best_action]
        
        # Generate combined rationale
        rationales = [f"{d.agent_name}: {d.rationale}" for d in decisions]
        combined_rationale = " | ".join(rationales)
        
        # Check for veto conditions
        risk_decision = next((d for d in decisions if d.agent_name == "RiskAgent"), None)
        if risk_decision and risk_decision.action == AgentAction.ALERT:
            best_action = AgentAction.HOLD
            combined_rationale = f"RISK VETO: {risk_decision.rationale}"
        
        return AgentDecision(
            agent_name=self.name,
            action=best_action,
            confidence=min(best_score, 1.0),
            rationale=combined_rationale,
            metadata={
                "sub_decisions": [d.to_dict() for d in decisions],
                "action_scores": {k.value: round(v, 3) for k, v in action_scores.items()},
                "research_report": context.research_report
            }
        )
    
    def act(self, decision: AgentDecision, context: AgentContext) -> AgentContext:
        """
        Optionally execute the trade if auto_execute is enabled.
        """
        if self.auto_execute and decision.action in [AgentAction.BUY, AgentAction.SELL]:
            # Find the execution decision and execute it
            exec_decision = next(
                (d for d in decision.metadata.get("sub_decisions", []) 
                 if d.get("agent") == "ExecutionAgent"),
                None
            )
            if exec_decision:
                context = self.execution_agent.act(
                    AgentDecision(
                        agent_name="ExecutionAgent",
                        action=AgentAction[exec_decision["action"]],
                        confidence=exec_decision["confidence"],
                        rationale=exec_decision["rationale"],
                        metadata=exec_decision.get("metadata", {})
                    ),
                    context
                )
        
        context.add_message(
            self.name,
            f"Pipeline complete: {decision.action.value} ({decision.confidence:.1%})",
            "INFO"
        )
        
        return context
    
    def run_pipeline(self, symbol: str, sentiment_score: float = 50.0) -> Dict[str, Any]:
        """
        Convenience method to run the full pipeline from scratch.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            sentiment_score: Fear & Greed index (0-100)
            
        Returns:
            Dict with final decision and all sub-decisions.
        """
        # Create fresh context
        context = AgentContext(
            symbol=symbol,
            sentiment_score=sentiment_score
        )
        
        # Run think -> act
        decision = self.think(context)
        context = self.act(decision, context)
        
        return {
            "final_decision": decision.to_dict(),
            "context_messages": context.messages,
            "research_report": context.research_report,
            "risk_assessment": context.risk_assessment,
            "ml_prediction": context.ml_prediction
        }


# Singleton for easy access
manager = ManagerAgent()
