"""
Strategy Engine

Orchestrates signals from multiple sources (ML, Sentiment, Risk) to generate 
actionable Trading Signals.

Architecture:
1. Signal Generation (ML Model, Technicals)
2. Signal Filter (Sentiment, Volatility)
3. Risk Filter (Risk Engine)
4. Final Decision
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from core.ml_models import DeepLOBLite

@dataclass
class TradingSignal:
    symbol: str
    action: str # BUY, SELL, HOLD
    confidence: float
    reason: str
    timestamp: str

class StrategyEngine:
    def __init__(self):
        self.ml_model = DeepLOBLite()
        # In a real system, we'd inject Dependencies like SentimentAnalyzer
        
    def generate_signal(self, symbol: str, bids: List[List[float]], asks: List[List[float]], sentiment_score: float = 50.0) -> Dict[str, Any]:
        """
        Combine ML prediction with Sentiment to form a strategy decision.
        
        Args:
            symbol: Asset symbol.
            bids: Current orderbook bids.
            asks: Current orderbook asks.
            sentiment_score: 0-100 (Fear & Greed).
            
        Returns:
            Dict representing the Signal.
        """
        # 1. ML Prediction (Microstructure)
        ml_res = self.ml_model.predict(bids, asks)
        ml_signal = ml_res["signal"] # UP, DOWN, STATIONARY
        ml_conf = ml_res["confidence"]
        
        # 2. Sentiment Filter (Macro)
        # Rule: Don't short in Extreme Greed? Or Follow trend?
        # Simple Strategy: Alignment. 
        # If ML says UP and Sentiment > 40 (Not Extreme Fear), BUY.
        # If ML says DOWN and Sentiment < 60 (Not Extreme Greed), SELL.
        
        action = "HOLD"
        reason = "Uncertain signal"
        final_conf = 0.0
        
        if ml_signal == "UP":
            if sentiment_score > 30: # Not extreme fear
                action = "BUY"
                reason = f"ML Bullish ({ml_conf:.2f}) + Sentiment Neutral/Bullish ({sentiment_score})"
                final_conf = ml_conf
            else:
                reason = "ML Bullish but Sentiment is Extreme Fear (Contrarian Risk)"
                
        elif ml_signal == "DOWN":
            if sentiment_score < 70: # Not extreme greed
                action = "SELL"
                reason = f"ML Bearish ({ml_conf:.2f}) + Sentiment Neutral/Bearish ({sentiment_score})"
                final_conf = ml_conf
            else:
                reason = "ML Bearish but Sentiment is Extreme Greed (Squeeze Risk)"
                
        else:
            reason = "Market Stationary"
            
        return {
            "symbol": symbol,
            "action": action,
            "confidence": round(final_conf, 3),
            "reason": reason,
            "ml_signal": ml_res,
            "sentiment_score": sentiment_score
        }

strategy_engine = StrategyEngine()
