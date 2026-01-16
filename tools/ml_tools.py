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
from core.analytics import OrderBook, MicrostructureAnalyzer

# Global analyzer for feature extraction
_analyzer = MicrostructureAnalyzer()

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
        
        Uses Order Flow Imbalance (OFI) and Order Book Imbalance (OBI) as primary features,
        calibrated to mimic DeepLOB's attention to liquidity distribution.
        
        Args:
            bids: List of [price, volume] pairs.
            asks: List of [price, volume] pairs.
            horizon_seconds: Prediction horizon (informational only for this lite model).
            
        Returns:
            JSON string with probabilities for [UP, DOWN, STATIONARY].
        """
        try:
            # 1. Feature Extraction
            book = OrderBook.from_raw(bids, asks, datetime.now())
            metrics = _analyzer.analyze(book)
            
            # Features
            ofi = metrics.ofi  # Order Flow Imbalance (-1 to 1 theoretical range, usually smaller)
            obi = metrics.obi  # Order Book Imbalance (-1 to 1)
            mp_divergence = metrics.microprice_divergence # Microprice - Midprice
            
            # 2. Inference Logic (DeepLOB Lite)
            # We use a calibrated logistic-style function based on HFT literature
            # OFI is the strongest predictor for immediate moves.
            # OBI is a sustaining factor.
            
            # Synthetic logits
            logit_up = (ofi * 2.5) + (obi * 1.5) + (mp_divergence * 100.0)
            logit_down = -(ofi * 2.5) - (obi * 1.5) - (mp_divergence * 100.0)
            logit_stationary = 2.0 - abs(logit_up) # Bias towards stationary if signal is weak
            
            # Softmax
            logits = np.array([logit_up, logit_stationary, logit_down])
            exp_logits = np.exp(logits - np.max(logits)) # Stability
            probs = exp_logits / np.sum(exp_logits)
            
            p_up, p_stat, p_down = probs
            
            # 3. Confidence & Signal
            if p_up > 0.45 and p_up > p_down:
                signal = "UP"
                confidence = p_up
            elif p_down > 0.45 and p_down > p_up:
                signal = "DOWN"
                confidence = p_down
            else:
                signal = "STATIONARY"
                confidence = p_stat
                
            return json.dumps({
                "signal": signal,
                "confidence": round(float(confidence), 3),
                "probabilities": {
                    "up": round(float(p_up), 3),
                    "stationary": round(float(p_stat), 3),
                    "down": round(float(p_down), 3)
                },
                "features": {
                    "ofi": metrics.ofi,
                    "obi": metrics.obi,
                    "microprice_div": round(metrics.microprice_divergence, 6)
                },
                "model": "DeepLOB_Lite_v1",
                "timestamp": datetime.now().isoformat()
            })
            
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
