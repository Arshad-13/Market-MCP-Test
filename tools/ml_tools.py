"""
AI Prediction Tools (DeepLOB Lite)

MCP tools for price direction prediction using lightweight quant models.
Adapts concepts from DeepLOB (Deep Limit Order Book) into a feature-based inference engine.
"""

import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from core.ml_models import DeepLOBLite

# Global model instance
_model = DeepLOBLite()

def register_ml_tools(mcp: FastMCP) -> None:
    """
    Register Machine Learning MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def predict_price_direction(
        bids: List[List[float]],
        asks: List[List[float]],
        horizon_seconds: int = 10
    ) -> str:
        """
        Predict short-term price direction using a lightweight ML-based heuristic model.
        
        Args:
            bids: List of [price, volume] pairs.
            asks: List of [price, volume] pairs.
            horizon_seconds: Prediction horizon (informational only).
            
        Returns:
            JSON string with probabilities for [UP, DOWN, STATIONARY].
        """
        try:
            # Delegate to core model
            result = _model.predict(bids, asks)
            
            # Add metadata
            result["model"] = "DeepLOB_Lite_v1"
            result["timestamp"] = datetime.now().isoformat()
            
            # JSON serialization formatting for floats (rounding for display)
            result["confidence"] = round(result["confidence"], 3)
            result["probabilities"] = {k: round(v, 3) for k, v in result["probabilities"].items()}
            result["features"]["microprice_div"] = round(result["features"]["microprice_div"], 6)
            
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({
                "error": "Prediction failed",
                "details": str(e)
            })

    @mcp.tool()
    def analyze_volatility_regime(
        prices: List[float]
    ) -> str:
        """
        Classify the volatility regime of a price series.
        
        Args:
            prices: List of recent prices (e.g., last 20-50 ticks or candles).
            
        Returns:
            JSON string with regime classification.
        """
        if len(prices) < 2:
            return json.dumps({"error": "Need at least 2 prices"})
            
        try:
            arr = np.array(prices)
            returns = np.diff(np.log(arr))
            volatility = np.std(returns) * np.sqrt(len(prices)) # Simplified 'realized vol' metric
            
            # Thresholds (Arbitrary for this heuristic, would be adaptive in full ML)
            if volatility < 0.001:
                regime = "LOW_VOLATILITY"
            elif volatility < 0.005:
                regime = "NORMAL_VOLATILITY"
            else:
                regime = "HIGH_VOLATILITY_BURST"
                
            return json.dumps({
                "regime": regime,
                "volatility_score": round(float(volatility), 6),
                "sample_size": len(prices),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return json.dumps({"error": "Analysis failed", "details": str(e)})
