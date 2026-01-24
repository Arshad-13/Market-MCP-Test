"""
Base Agent - Abstract Interface for All Agents

Defines the core contract (think, act) and shared data structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

class AgentAction(Enum):
    """Possible actions an agent can recommend."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    RESEARCH = "RESEARCH"  # Need more info
    ALERT = "ALERT"        # Flag for human review


@dataclass
class AgentContext:
    """Shared context passed between agents in a pipeline."""
    symbol: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Market Data (populated by Research/Manager)
    price: Optional[float] = None
    bids: List[List[float]] = field(default_factory=list)
    asks: List[List[float]] = field(default_factory=list)
    sentiment_score: Optional[float] = None  # 0-100
    
    # Analysis Results (populated by specialized agents)
    risk_assessment: Optional[Dict[str, Any]] = None
    ml_prediction: Optional[Dict[str, Any]] = None
    research_report: Optional[str] = None
    
    # Execution State
    current_position: float = 0.0
    available_capital: float = 0.0
    
    # Agent Communication
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_message(self, agent_name: str, content: str, priority: str = "INFO"):
        """Add a message from an agent to the shared context."""
        self.messages.append({
            "agent": agent_name,
            "content": content,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        })


@dataclass
class AgentDecision:
    """Output of an agent's think() method."""
    agent_name: str
    action: AgentAction
    confidence: float  # 0.0 to 1.0
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "action": self.action.value,
            "confidence": round(self.confidence, 3),
            "rationale": self.rationale,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Each agent must implement:
    - think(context): Analyze the context and produce a decision
    - act(decision): Execute or apply the decision
    """
    
    def __init__(self, name: str):
        self.name = name
        self._is_active = True
    
    @abstractmethod
    def think(self, context: AgentContext) -> AgentDecision:
        """
        Analyze the shared context and produce a decision.
        
        Args:
            context: Shared AgentContext with market data and state.
            
        Returns:
            AgentDecision with recommended action and rationale.
        """
        pass
    
    @abstractmethod
    def act(self, decision: AgentDecision, context: AgentContext) -> AgentContext:
        """
        Execute or apply the decision, updating the context.
        
        Args:
            decision: The decision from think().
            context: Shared context to update.
            
        Returns:
            Updated AgentContext.
        """
        pass
    
    def run(self, context: AgentContext) -> AgentContext:
        """
        Convenience method: think then act.
        """
        decision = self.think(context)
        return self.act(decision, context)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
