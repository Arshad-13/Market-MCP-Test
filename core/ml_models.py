"""
Machine Learning Models

Core inference logic for price prediction and regime classification.
Separated from tools to allow internal use by StrategyEngine.
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Tuple

from core.analytics import OrderBook, MicrostructureAnalyzer

class DeepLOBLite:
    """
    Lightweight heuristic model inspired by DeepLOB.
    Predicts price direction (UP/DOWN/STATIONARY) based on OFI and OBI.
    """
    def __init__(self):
        self.analyzer = MicrostructureAnalyzer()

    def predict(self, bids: List[List[float]], asks: List[List[float]]) -> Dict[str, Any]:
        """
        Run inference on a raw order book snapshot.
        """
        # 1. Feature Extraction
        book = OrderBook.from_raw(bids, asks, datetime.now())
        metrics = self.analyzer.analyze(book)
        
        ofi = metrics.ofi
        obi = metrics.obi
        mp_divergence = metrics.microprice_divergence
        
        # 2. Inference Logic (Calibrated Heuristic)
        # Weights derived from HFT literature patterns
        logit_up = (ofi * 2.5) + (obi * 1.5) + (mp_divergence * 100.0)
        logit_down = -(ofi * 2.5) - (obi * 1.5) - (mp_divergence * 100.0)
        logit_stationary = 2.0 - abs(logit_up) # Bias towards stationary
        
        # Softmax
        logits = np.array([logit_up, logit_stationary, logit_down])
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        
        p_up, p_stat, p_down = probs
        
        # 3. Signal Generation
        if p_up > 0.45 and p_up > p_down:
            signal = "UP"
            confidence = p_up
        elif p_down > 0.45 and p_down > p_up:
            signal = "DOWN"
            confidence = p_down
        else:
            signal = "STATIONARY"
            confidence = p_stat
            
        return {
            "signal": signal,
            "confidence": float(confidence),
            "probabilities": {
                "up": float(p_up),
                "stationary": float(p_stat),
                "down": float(p_down)
            },
            "features": {
                "ofi": ofi,
                "obi": obi,
                "microprice_div": mp_divergence
            }
        }
